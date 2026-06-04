# Projeto-Grafos-Avd

Como Rodar o Projeto (Guia Rápido)
Pré-requisitos: Certifique-se de ter o Node.js e o Python 3.11+ instalados na sua máquina.

1. Iniciando o Backend (API Flask)
Abra o seu terminal e execute os seguintes comandos em ordem:

```Bash
# Entre na pasta do backend
cd backend

# Crie e ative um ambiente virtual
python -m venv venv
# Se estiver no Windows: venv\Scripts\activate
# Se estiver no Mac/Linux: source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Inicie o servidor
python src/app.py
2. Iniciando o Frontend (React/Vite)
Abra uma nova aba no seu terminal (mantenha o backend rodando na anterior) e execute:

Bash
# Entre na pasta do frontend
cd frontend

# Instale as dependências do Node
npm install

# Inicie o servidor de desenvolvimento
npm run dev
``` 

Pronto! Agora é só clicar no link gerado no terminal do frontend (geralmente http://localhost:5173) ou acessar no seu navegador. O projeto estará rodando localmente com o grafo interativo e a API conectada.