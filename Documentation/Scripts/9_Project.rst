Fine-tuning Mistral avec Unsloth pour l'Analyse Médicale
================================================

Nous avons implanté un modèle Mistral optimisé pour l'analyse de résultats médicaux en utilisant Unsloth.

Installation
-----------

.. code-block:: python

    pip install unsloth
    pip uninstall unsloth -y && pip install --upgrade --no-cache-dir --no-deps git+https://github.com/unslothai/unsloth.git

Configuration initiale
--------------------

1. Initialisation du modèle:

.. code-block:: python

    from unsloth import FastLanguageModel
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = "unsloth/mistral-7b-v0.3",
        max_seq_length = 2048,
        load_in_4bit = True
    )

2. Configuration PEFT:

.. code-block:: python

    model = FastLanguageModel.get_peft_model(
        model,
        r = 16,
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                         "gate_proj", "up_proj", "down_proj"],
        lora_alpha = 16,
        use_gradient_checkpointing = "unsloth"
    )

Préparation des données
---------------------

Dataset utilisé: ``Nassira/MedAnalyzr``

Format du prompt:

.. code-block:: python

    alpaca_prompt = """Vous êtes un médecin professionnel spécialisé dans l'analyse des résultats de laboratoire médical...

    ### Instruction:
    {}

    ### Input:
    {}

    ### Response:
    {}"""

Paramètres d'entraînement
------------------------

* Batch size: 2
* Gradient accumulation: 4
* Learning rate: 2e-4
* Epochs: 1
* Optimiseur: adamw_8bit

Utilisation
----------

.. code-block:: python

    FastLanguageModel.for_inference(model)
    inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=128)
    response = tokenizer.batch_decode(outputs)[0]

Optimisations
-----------

1. Quantification 4-bit
2. Gradient checkpointing avec mode "unsloth"
3. LoRA avec r=16
4. Batch processing optimisé

Résultats
--------

* Loss finale: ~0.3
* Temps d'entraînement: ~34 minutes pour 272 steps
