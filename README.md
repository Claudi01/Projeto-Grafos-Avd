# Como Rodar o Projeto (Guia Atualizado)

**Pré-requisitos:** Certifique-se de ter o Node.js (com a variável PATH configurada) e o Python 3.11+ instalados na sua máquina.

### 1. Atualizando as Dependências
Antes de iniciar os servidores, certifique-se de que o arquivo `requirements.txt` localizado na **raiz do projeto** (`PROJETO-GRAFOS-AVD/`) contém as seguintes bibliotecas:
\`\`\`text
pandas
pytest
matplotlib
pyvis
plotly
streamlit
flask
flask-cors
\`\`\`

### 2. Iniciando o Backend (API Flask)
Abra o seu terminal na **raiz do projeto** e execute os seguintes comandos em ordem:

\`\`\`bash
# Entre na subpasta do backend
cd parte2/backend

# Ative o ambiente virtual
# Se estiver no Windows: 
.\venv\Scripts\activate
# Se estiver no Mac/Linux: 
source venv/bin/activate

# Instale as dependências (buscando o arquivo na raiz do projeto)
pip install -r ../../requirements.txt

# Inicie o servidor como um módulo do Python
py -m src.app
# (Nota: se 'py' não funcionar, utilize 'python -m src.app')
\`\`\`
O servidor ficará rodando (geralmente em `http://127.0.0.1:5000/`). **Mantenha este terminal aberto.**

### 3. Iniciando o Frontend (React/Vite)
Abra uma **nova aba** ou um **novo terminal** (também a partir da raiz do projeto) e execute:

\`\`\`bash
# Entre na subpasta do frontend
cd parte2/frontend

# Instale as dependências do Node
npm install

# Inicie o servidor de desenvolvimento
npm run dev
\`\`\`

**Pronto!** Agora é só segurar o `Ctrl` e clicar no link gerado no terminal do frontend (geralmente `http://localhost:5173`) ou acessar diretamente no seu navegador. O projeto estará rodando localmente com o grafo interativo e a API conectada.

---
**Como encerrar a aplicação:**
Para parar os servidores, basta ir em cada um dos terminais abertos e pressionar `Ctrl + C`. No terminal do backend, você também pode digitar `deactivate` para sair do ambiente virtual do Python.