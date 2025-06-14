# -*- coding: utf-8 -*-
"""Pipeline

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/184HYQmeblTnQvtbsdhQvqmUw5EedIXPR
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, roc_auc_score
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree

def preprocess_and_train(df, target_col='falha'):
    # --- Tratamento básico e limpeza ---
    # Converter colunas de data
    date_cols = [
        'datahora_abertura_solicitacao', 'datahora_audiencia', 'datahora_finalizacao_solicitacao'
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    # Criar features temporais
    df['antecedencia_dias'] = (df['datahora_audiencia'] - df['datahora_abertura_solicitacao']).dt.days
    df['duracao_abertura_finalizacao'] = (df['datahora_finalizacao_solicitacao'] - df['datahora_abertura_solicitacao']).dt.days
    df['mes_audiencia'] = df['datahora_audiencia'].dt.month

    # Seleção inicial de features (excluindo IDs e target)
    features = [
        'nome_parceiro', 'nome_cliente', 'tipo', 'tipo_demanda', 'area_processo',
        'tipo_audiencia', 'situacao', 'orgao', 'comarca', 'uf_comarca',
        'situacao_dados', 'orientacoes_inseridas_cliente', 'qtd_troca',
        'qtd_declinio', 'houve_revelia', 'houve_ausencia', 'houve_ma_atuacao',
        'mes_audiencia', 'duracao_abertura_finalizacao', 'antecedencia_dias'
    ]

    # Preencher NaNs nas features numéricas com 0 (ou outro método)
    df[features] = df[features].fillna(0)

    # Codificar variáveis categóricas com LabelEncoder
    cat_cols = [
        'nome_parceiro', 'nome_cliente', 'tipo', 'tipo_demanda', 'area_processo',
        'tipo_audiencia', 'situacao', 'orgao', 'comarca', 'uf_comarca',
        'situacao_dados', 'orientacoes_inseridas_cliente'
    ]
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))

    # Separar X e y
    X = df[features]
    y = df[target_col]

    # Dividir treino/teste com stratify para manter proporções da target
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, stratify=y, test_size=0.2, random_state=42
    )

    # Pipeline com SMOTE + Decision Tree
    pipeline = Pipeline([
        ('smote', SMOTE(random_state=42)),
        ('clf', DecisionTreeClassifier(random_state=42, max_depth=4, class_weight='balanced'))
    ])

    # Treinar
    pipeline.fit(X_train, y_train)

    # Previsões
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    # Avaliação
    print("Classificação:\n", classification_report(y_test, y_pred))
    print("AUC ROC:", roc_auc_score(y_test, y_proba))

    # Plot árvore para interpretabilidade
    plt.figure(figsize=(20,10))
    plot_tree(pipeline.named_steps['clf'], feature_names=features,
              class_names=['No Fail', 'Fail'], filled=True, rounded=True)
    plt.show()

    return pipeline

# Uso:
# df = pd.read_csv('seu_arquivo.csv')
# model = preprocess_and_train(df, target_col='falha')