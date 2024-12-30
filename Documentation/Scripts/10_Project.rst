Fine-tuning des Embeddings pour des Domaines Spécifiques (Analyse Médicale)
========================================================================

Introduction
-----------
Imaginez que vous construisez un système de question-réponse pour le domaine médical. Vous voulez vous assurer qu'il puisse récupérer avec précision les articles médicaux pertinents lorsqu'un utilisateur pose une question. Mais les modèles d'embedding génériques pourraient avoir du mal avec le vocabulaire hautement spécialisé et les nuances de la terminologie médicale.

C'est là que le fine-tuning entre en jeu !

Les Embeddings
-------------
Les embeddings sont de puissantes représentations numériques de texte ou d'image qui capturent les relations sémantiques. Les applications principales incluent:

* Semantic Similarity
* Text Classification
* Question Answering
* Retrieval Augmented Generation (RAG)

Matryoshka Representation Learning
--------------------------------
Le Matryoshka Representation Learning (MRL) est une technique pour créer des vecteurs d'embedding "truncatables". Le MRL embarque le texte de manière hiérarchique:

1. Les premières dimensions contiennent les informations essentielles
2. Les dimensions suivantes ajoutent des détails
3. Permet une réduction dimensionnelle flexible

Configuration du Modèle
----------------------
.. code-block:: python

    from transformers import AutoModel, AutoTokenizer

    model_name = "intfloat/multilingual-e5-large"
    model = AutoModel.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

Caractéristiques du Modèle
-------------------------
* Nom: intfloat/multilingual-e5-large
* Architecture: 12 couches
* Taille d'embedding: 384 dimensions
* Publication: "Multilingual E5 Text Embeddings: A Technical Report" (Wang et al., 2024)

Formats de Dataset
-----------------
Plusieurs formats sont supportés pour le fine-tuning:

1. Positive Pair
    * Format: paires de phrases liées
    * Exemple: question-réponse

2. Triplets
    * Format: (ancre, positif, négatif)
    * Usage: apprentissage contrastif

3. Pair with Similarity Score
    * Format: paire + score
    * Usage: apprentissage supervisé

4. Texts with Classes
    * Format: texte + classe
    * Usage: classification

Fonctions de Perte
-----------------
Les fonctions disponibles incluent:

Triplet Loss
^^^^^^^^^^^
.. code-block:: python

    def triplet_loss(anchor, positive, negative, margin=1.0):
        return max(0, margin + d(anchor, positive) - d(anchor, negative))

Contrastive Loss
^^^^^^^^^^^^^^^
Pour les paires positives et négatives.

Cosine Similarity Loss
^^^^^^^^^^^^^^^^^^^^
Pour les paires avec scores de similarité.

Matryoshka Loss
^^^^^^^^^^^^^
Spécialisée pour les embeddings Matryoshka truncatables.


Analyse des Performances
----------------------

Comparaison des Performances Avant et Après Fine-Tuning
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Le tableau suivant résume les scores NDCG@10 avant et après le fine-tuning pour différentes dimensions:

.. list-table:: Scores NDCG@10
   :header-rows: 1
   :widths: 15 25 25 20

   * - Dimension
     - Avant Fine-Tuning
     - Après Fine-Tuning
     - Amélioration
   * - **1024**
     - 0.7967
     - 0.8484
     - **+0.0517**
   * - **768**
     - 0.7981
     - 0.8464
     - **+0.0483**
   * - **512**
     - 0.7897
     - 0.8471
     - **+0.0574**
   * - **256**
     - 0.7522
     - 0.8383
     - **+0.0861**
   * - **128**
     - 0.6081
     - 0.8253
     - **+0.2172**
   * - **64**
     - 0.5182
     - 0.7858
     - **+0.2676**

Observations Clés
^^^^^^^^^^^^^^^^

1. Amélioration Globale
"""""""""""""""""""""""
* Le fine-tuning a conduit à une amélioration significative pour toutes les dimensions
* Les dimensions inférieures (64 et 128) montrent la plus grande amélioration relative
* Compression efficace de l'information dans des embeddings plus petits

2. Performance des Dimensions Élevées
"""""""""""""""""""""""""""""""""""
* Les meilleurs scores absolus sont observés dans les dimensions supérieures (1024, 768, 512)
* Ces embeddings capturent une information plus riche
* Rendements décroissants observés dans les dimensions supérieures

3. Recommandations Pratiques
"""""""""""""""""""""""""
* **Pour l'équilibre performance/efficacité**: Utiliser la dimension 512
* **Pour la performance maximale**: Opter pour la dimension 1024
* **Pour les ressources limitées**: La dimension 256 offre un bon compromis

Conclusion
^^^^^^^^^
L'analyse des performances démontre que:

* Le fine-tuning améliore substantiellement les scores NDCG@10
* Le choix de la dimension dépend des contraintes de déploiement
* Un compromis optimal peut être trouvé selon les besoins spécifiques

Résultats
---------
* Performance multilingue améliorée
* Réduction des coûts de stockage
* Meilleure précision dans le domaine médical

Notes d'Utilisation
------------------
1. Choisir le format de dataset approprié
2. Adapter la fonction de perte
3. Ajuster les hyperparamètres selon les besoins
4. Valider sur un ensemble de test spécifique au domaine


Implémentation
-------------

Chargement du Dataset
^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    from datasets import load_dataset
    
    # Load the dataset directly from Hugging Face Hub
    dataset = load_dataset("ilyass20/MedAnalyzer")

Chargement du Modèle
^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    import torch
    from sentence_transformers import SentenceTransformer
    from sentence_transformers.evaluation import (
        InformationRetrievalEvaluator,
        SequentialEvaluator,
    )
    from sentence_transformers.util import cos_sim
    from datasets import load_dataset, concatenate_datasets
    from sentence_transformers.losses import MatryoshkaLoss, MultipleNegativesRankingLoss

    model_id = "intfloat/multilingual-e5-large"
    
    # Load a model
    model = SentenceTransformer(
        model_id, device="cuda" if torch.cuda.is_available() else "cpu"
    )

Configuration de la Fonction de Perte
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    # Important: large to small
    matryoshka_dimensions = [1024, 768, 512, 256, 128, 64]
    inner_train_loss = MultipleNegativesRankingLoss(model)
    train_loss = MatryoshkaLoss(
        model, inner_train_loss, matryoshka_dims=matryoshka_dimensions
    )

Configuration des Arguments d'Entraînement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    from sentence_transformers import SentenceTransformerTrainingArguments
    from sentence_transformers.training_args import BatchSamplers

    args = SentenceTransformerTrainingArguments(
        output_dir="bge-finetuned",                   # output directory
        num_train_epochs=1,                           # number of epochs
        per_device_train_batch_size=4,                # train batch size
        gradient_accumulation_steps=16,               # global batch size of 512
        per_device_eval_batch_size=16,                # evaluation batch size
        warmup_ratio=0.1,                             # warmup ratio
        learning_rate=2e-5,                           # learning rate
        lr_scheduler_type="cosine",                   # scheduler type
        optim="adamw_torch_fused",                    # optimizer
        bf16=True,                                    # precision
        batch_sampler=BatchSamplers.NO_DUPLICATES,    # sampling strategy
        eval_strategy="epoch",                        # evaluation frequency
        save_strategy="epoch",                        # save frequency
        logging_steps=10,                             # logging frequency
        save_total_limit=3,                           # save limit
        load_best_model_at_end=True,                  # load best model
        metric_for_best_model="eval_dim_128_cosine_ndcg@10",
    )

Création de l'Évaluateur
^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    # Préparation des données
    corpus = dict(
        zip(range(len(dataset['train']['positive'])),
            dataset['train']['positive'])
    )

    queries = dict(
        zip(range(len(dataset['train']['anchor'])),
            dataset['train']['anchor'])
    )

    # Mapping des documents pertinents
    relevant_docs = {}
    for q_id in queries:
        relevant_docs[q_id] = [q_id]

    # Création des évaluateurs pour chaque dimension
    matryoshka_evaluators = []
    for dim in matryoshka_dimensions:
        ir_evaluator = InformationRetrievalEvaluator(
            queries=queries,
            corpus=corpus,
            relevant_docs=relevant_docs,
            name=f"dim_{dim}",
            truncate_dim=dim,
            score_functions={"cosine": cos_sim},
        )
        matryoshka_evaluators.append(ir_evaluator)

    evaluator = SequentialEvaluator(matryoshka_evaluators)

Évaluation Initiale du Modèle
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    results = evaluator(model)
    
    for dim in matryoshka_dimensions:
        key = f"dim_{dim}_cosine_ndcg@10"
        print(f"{key}: {results[key]}")

Configuration et Lancement de l'Entraînement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    from sentence_transformers import SentenceTransformerTrainer

    trainer = SentenceTransformerTrainer(
        model=model,
        args=args,
        train_dataset=dataset.select_columns(["anchor", "positive"]),
        loss=train_loss,
        evaluator=evaluator,
    )

    # Lancement de l'entraînement
    trainer.train()
    trainer.save_model()

Évaluation Après Fine-tuning
^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    from sentence_transformers import SentenceTransformer

    fine_tuned_model = SentenceTransformer(
        args.output_dir, 
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    
    # Évaluation du modèle
    results = evaluator(fine_tuned_model)

    # Affichage des résultats
    for dim in matryoshka_dimensions:
        key = f"dim_{dim}_cosine_ndcg@10"
        print(f"{key}: {results[key]}")
