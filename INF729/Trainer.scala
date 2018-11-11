package com.sparkProject

import org.apache.spark.SparkConf
import org.apache.spark.sql.functions._
import org.apache.spark.sql.{DataFrame, SaveMode, SparkSession}
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.Row
import org.apache.spark.ml.feature.{HashingTF, Tokenizer,  RegexTokenizer, StopWordsRemover, CountVectorizerModel,
  CountVectorizer, IDF, StringIndexer, OneHotEncoder, VectorAssembler}
import org.apache.spark.ml.{Pipeline}
import org.apache.spark.ml.classification.LogisticRegression
import org.apache.spark.ml.tuning.{CrossValidator, CrossValidatorModel, ParamGridBuilder}
import org.apache.spark.ml.evaluation.MulticlassClassificationEvaluator
import org.apache.spark.ml.evaluation.BinaryClassificationEvaluator

object Trainer {

  def main(args: Array[String]): Unit = {

    val conf = new SparkConf().setAll(Map(
      "spark.scheduler.mode" -> "FIFO",
      "spark.speculation" -> "false",
      "spark.reducer.maxSizeInFlight" -> "48m",
      "spark.serializer" -> "org.apache.spark.serializer.KryoSerializer",
      "spark.kryoserializer.buffer.max" -> "1g",
      "spark.shuffle.file.buffer" -> "32k",
      "spark.default.parallelism" -> "12",
      "spark.sql.shuffle.partitions" -> "12",
      "spark.driver.maxResultSize" -> "2g"
    ))

    val spark = SparkSession
      .builder
      .config(conf)
      .appName("TP_spark")
      .getOrCreate()

    import spark.implicits._

    /*******************************************************************************
      *
      *       TP 3 - Stéphane Mulard
      *
      *       - lire le fichier sauvegarder précédemment
      *       - construire les Stages du pipeline, puis les assembler
      *       - trouver les meilleurs hyperparamètres pour l'entraînement du pipeline avec une grid-search
      *       - Sauvegarder le pipeline entraîné
      *
      *       if problems with unimported modules => sbt plugins update
      *
      ********************************************************************************/

       // 1) Charger le fichier parquet dans le dataframe

    val df: DataFrame = spark
      .read
      .option("header", true)  // Use first line of all files as header
      .option("inferSchema", "true") // Try to infer the data types of each column
      .parquet("prepared_trainingset")

    // On peut afficher les infos du df récupéré si on veut.
    // df.describe().show();
    // df.show(10);

    // Avant de faire le split on va exécuter les stringIndexer et OneHotEncoder
    // Sinon il y a des risques que certaines valeurs ne soient pas présentes dans
    // le jeu de test à cause de la distribution des valeurs. En effet, certains
    // pays ou monnaies sont très peu représentés dans le set, ce qui peut provoquer
    // des erreurs et obligeait à mettre des setHandleInvalid("skip").

    // On transforme les valeurs textuelles catégoriques des pays (ex. USA, FR, etc.)
    // en données numériques, ex. 1, 2, 3, etc. dont le choix est basé sur la fréquence
    // d'occurences, 1 =  plus fréquent, 2 =  second plus fréquent, etc.
    val strIndexerCountry = new StringIndexer()
      .setInputCol("country2")
      .setOutputCol("country_indexed2")
      //.setHandleInvalid("keep")

    // Idem pour les valeurs de currency (USD, EUR, etc.)
    val strIndexerCurrency = new StringIndexer()
      .setInputCol("currency2")
      .setOutputCol("currency_indexed2")
      //.setHandleInvalid("keep")

    // Le OneHotEncoder ajoute autant de colonnes que de valeurs distinctes
    // dans la colonne "country_indexed" et remplit avec 1 ou 0 selon la valeur
    val countryEncoder = new OneHotEncoder()
      .setInputCol("country_indexed2")
      .setOutputCol("country_indexed")

    // Idem en ajoutant autant de colonnes que de currency différentes
    val currencyEncoder = new OneHotEncoder()
      .setInputCol("currency_indexed2")
      .setOutputCol("currency_indexed")

    // Premier pipeline de traitement
    val pipeline1 = new Pipeline()
      .setStages(Array(strIndexerCountry, strIndexerCurrency,
        countryEncoder,currencyEncoder))

    val model = pipeline1.fit(df)
    val dfprocessed = model.transform(df)

    //On peut maintenant séparer les données en jeu d'entraînement et jeu de test
    val splits = dfprocessed.randomSplit(Array(0.9, 0.1))
    val dftraining = splits(0)
    val dftest = splits(1)

    println("Pré-traitement et split terminés !")

    // 2 Utilisez les données textuelles

    // séparation du textes en mots (token) avec le Tokenizer
    val tokenizer = new RegexTokenizer()
      .setPattern("\\W+") // pattern = mots
      .setGaps(true)
      .setInputCol("text")
      .setOutputCol("tokens") // résultat dans la colonne tokens

    // Pour vérifier on peut lancer la fonction Transform() et récupérer un DataFrame
    // val dftoken = tokenizer.transform(df)

    // On retire les "petits" mots ou mots de liaison sans grande signification avec
    // le StopWordsRemover
    val remover = new StopWordsRemover()
      .setInputCol("tokens")
      .setOutputCol("wordsremoved")

    // Idem pour vérifier si on veut afficher le résultat de cette transformation
    //val dfremove = remover.transform(dftoken)

    // On calcule la fréquence de chaque terme pour chaque ligne de la colonne
    // (normalisée par le nombre de mots sur la ligne)
    // obtenue après retrait des petits mots, i.e. wordsremoved
    // Attention ici il y a un hyper-paramètre à régler, MinDF, et qui correspond
    // à la fréquence minimale d'apparition des mots dans le texte pour être pris en compte
    val countVectorizer: CountVectorizer = new CountVectorizer()
      .setInputCol("wordsremoved")
      .setOutputCol("tf")

    // On calcul la donnée tfIdf pour chaque mot du corpus
    // soit tf*idf où idf représente l'inverse de la fréquence des termes dans tout le corpus
    // Dans la colonne tfifd, il y a en fait autant de "colonnes" que de mots uniques du corpus.
    // Ces valeurs sont stockées en format "sparse", c'est à dire :
    // (NbTotalMots, [indices des valeurs non nulles] [valeurs non nulles])
    // ex. (10000, [2, 350, 400...] [0,5, 0,22, 0.8...]
    val idf = new IDF()
      .setInputCol("tf")
      .setOutputCol("tfidf")

    // Si on souhaite visualiser le résultat de la dernière transformation
    // dftransformed.select("tfidf").show()
    // Si on souhaite voir quel terme correspond à un indice donné
    // val cv: CountVectorizerModel = model.stages(2).asInstanceOf[CountVectorizerModel]
    // println(cv.vocabulary(33))

    // On regroupe les données (toutes nos colonnes) dans une seule colonne de features
    // car c'est ainsi que SparkML peut interpréter et travailler par la suite
    val assembler = new VectorAssembler()
      .setInputCols(Array("tfidf", "days_campaign", "hours_prepa", "goal", "country_indexed","currency_indexed"))
      .setOutputCol("features")

    // On définit nos paramètres de la regression logistique qui est notre algorithme d'apprentissage
    // et de classification des données en 0 = échec ou 1 succès de financement prédit
    // plusieurs hyper paramètres sont à régler, threshold, tolérance, max itérations, etc.
    // le threshold correspond à la valeur de probabilité qui décide de la classification
    // ici, avec une valeur à 0,3 on dit que si la probabilité trouvée est supérieure à 0,3,
    // on classifie que la campagne est un succès... cela signifie que l'on est "optimiste" :
    // il se peut qu'on prédise plus de succès qu'il y en a en réalité, mais par contre on
    // s'assure de trouver tous les succès... c'est un choix "métier". Avec un seuil à 0,7
    // par exemple, on serait plus sévère :  on serait plus certain que chaque succès prédit
    // serait un vrai succès, mais on risquerait d'éliminer certain vrais succès.
    val lr = new LogisticRegression()
      .setElasticNetParam(0.0)
      .setFitIntercept(true)
      .setFeaturesCol("features")
      .setLabelCol("final_status")
      .setStandardization(true)
      .setPredictionCol("predictions")
      .setRawPredictionCol("raw_predictions")
      .setThresholds(Array(0.6, 0.4))
      .setTol(1.0e-6)
      .setMaxIter(300)

    // On met bout à bout toutes les étapes (stages) de transformation définies précédemment
    // dans un Pipeline
    val pipeline2 = new Pipeline()
      .setStages(Array(tokenizer, remover, countVectorizer, idf, assembler,lr))

    // On définit la grille de recherche pour les hyper-paramètres optimaux
    // Pour la régularisation de la régression logistique on veut tester les valeurs
    // de 10e-8 à 10e-2 par pas de 2.0 en échelle logarithmique
    // Pour le paramètre minDF de countVectorizer on veut tester
    // les valeurs de 55 à 95 par pas de 20
    val paramGrid = new ParamGridBuilder()
      .addGrid(countVectorizer.minDF, Array(55.0, 75.0, 95.0))
      .addGrid(lr.regParam, Array(10.0e-8, 10.0e-6, 10.0e-4, 10.0e-2))
      .build()

    // On définit la manière dont on va évaluer notre cross-validation en définissant
    // un évaluateur, ici le score f1
    val binEvaluator = new MulticlassClassificationEvaluator()
      .setMetricName("f1")
      .setLabelCol("final_status")
      .setPredictionCol("predictions")

    // On définit notre cross-validator en lui passant les objets créés précédemment :
    // le pipeline, l'évaluateur, la grille de paramètre, le nombre de fold
    // avec 3 folds on s'entraine sur 2/3 des données de training et on valide sur 1/3
    val cv = new CrossValidator()
      .setEstimator(pipeline2)
      .setEvaluator(binEvaluator)
      .setEstimatorParamMaps(paramGrid)
      .setNumFolds(3)

    //On lance l'apprentissage avec la méthode fit sur les données de training
    val cvModel = cv.fit(dftraining)

    println("Cross-validation terminée !")

    // puis on applique le modèle sur nos données de test
    // et on récupère le DataFrame avec les prédictions de chaque campagne.
    val df_WithPredictions = cvModel.transform(dftest)

    // Pour vérifier, on affiche l'identifiant, le nom, le vrai statut et la prédiction des campagnes
    df_WithPredictions.select("project_id", "name","final_status", "predictions").show()

    // On groupe par final_Status et prédiction pour comparer les nombres
    // entre la vraie valeur et la prédiction
    df_WithPredictions.groupBy("final_status", "predictions").count.show()

    // On définit un évaluateur pour obtenir une mesure de la performane
    val test_evaluator = new MulticlassClassificationEvaluator()
      .setLabelCol("final_status")
      .setPredictionCol("predictions")
      .setMetricName("f1")

    val f1Score = test_evaluator.evaluate(df_WithPredictions)

    println(f"Score F1 : $f1Score%.2f")

    //On sauvegarde le dataframe final pour pouvoir l'étudier séparément si nécessaire
    df_WithPredictions.write.mode(SaveMode.Overwrite)
                .parquet("test_results")

    //On enregistre le modèle entraîné
    cvModel.write.overwrite().save("kickstarterModel")
  }
}
