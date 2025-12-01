# LiriRack-pip

# . . .  DESCRICAO . . . 
-> Sistema para análise automatizada de históricos acadêmicos da UEPB em formato PDF

-> Linguagem: Python 
-> dependencia: Pip
-> bibliotecas: 
    - pdfplumber: extração de dados do PDF
    - pandas: análise e manipulação de dados
    - plotly: visualizações interativas
    - streamlit: interface web

# . .  grupo . .
-> Raquel: Backend - finalizada
-> Liriel: frontend - iniciando


# . .  Turma . .
ADS2

## 🐳 Docker

### Opção 1: Usar a imagem publicada (RECOMENDADO)
```bash
docker pull ghcr.io/rcrislane/lirirack-pip:latest
docker run -p 8501:8501 ghcr.io/rcrislane/lirirack-pip:latest
```

Acesse: http://localhost:8501

# . .  . < Opção 2: Buildar localmente > ..  .

git clone https://github.com/RCrislane/LiriRack-pip.git
cd LiriRack-pip
docker build -t lirirack-pip .
docker run -p 8501:8501 lirirack-pip

Acesse: http://localhost:8501