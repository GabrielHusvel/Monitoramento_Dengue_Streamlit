from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, roc_curve
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn import svm
from sklearn.metrics import roc_auc_score


df_rio = pd.read_csv('../data_sus\PySUS\infodengue\dengue_rio_de_janeiro_2010_2024.csv')
df_rio.info()
df_rio = df_rio.dropna()

# Se 'data_iniSE' for uma data, converter para datetime
df_rio['data_iniSE'] = pd.to_datetime(df_rio['data_iniSE'])

# Separar as features (X) e o alvo (y)
X = df_rio.drop(columns=['casos', 'data_iniSE'])
y = df_rio['casos']

# Dividir em conjunto de treinamento e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Escalonar os dados (importante para modelos como regressão linear e gradient boosting)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Treinamento do modelo Random Forest
rf_model = RandomForestRegressor(random_state=42, n_estimators=100, criterion='gini')
rf_model.fit(X_train, y_train)

# Previsões
y_pred_rf = rf_model.predict(X_test)

# Avaliação com classification report (considerando o valor real como contínuo)
print('Random Forest Regressor')
print(classification_report(y_test.round(), y_pred_rf.round()))

# Treinamento do modelo de Regressão Linear
lr_model = LinearRegression()
lr_model.fit(X_train_scaled, y_train)

# Previsões
y_pred_lr = lr_model.predict(X_test_scaled)

# Avaliação com classification report
print('Regressão Linear')
print(classification_report(y_test.round(), y_pred_lr.round()))

# Treinamento do modelo Gradient Boosting
gb_model = GradientBoostingRegressor(random_state=42)
gb_model.fit(X_train_scaled, y_train)

# Previsões
y_pred_gb = gb_model.predict(X_test_scaled)

# Avaliação com classification report
print('Gradient Boosting Regressor')
print(classification_report(y_test.round(), y_pred_gb.round()))


# Supondo que y seja o número de casos, definimos um limiar, por exemplo, a média
threshold = y.mean()

# Transformar em problema binário
y_test_binary = (y_test > threshold).astype(int)


# ROC AUC para Regressão Linear
roc_auc_lr = roc_auc_score(y_test_binary, y_pred_lr)
print('Regressão Linear ROC AUC:', roc_auc_lr)


