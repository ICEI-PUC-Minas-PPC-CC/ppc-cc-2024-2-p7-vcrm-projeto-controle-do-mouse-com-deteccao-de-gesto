# Trabalho de Visão Computacional

Implementação do trabalho de Visão Computacional

## Requisitos

| Nome | Versão |
-------|---------
Python | `3.12.2`

## Instalação

- Inicie um ambiente virtual:

    ```sh
    python3.12 -m venv venv
    ```

- Ative o ambiente virtual:

    ```sh
    source venv/bin/activate
    ```

- Instale as dependências:

    ```sh
    pip install -r ./requirements.txt
    ```

## Execução

Execute a aplicação com:

```sh
python main.py
```

## API

Antes de executar o projeto chamando a API, siga os passos na [Instalação](#instalação).

- Em um terminal, inicie o servido:

    ```sh
    python api.py
    ```

- Em outro terminal, inicie o cliente:

    ```sh
    python client.py
    ```

## Diferença

Ao executar um cliente, que chama a API, o funcionamento será o mesmo que a versão sem API.
A diferença está na implementação. A versão sem API é um programa rodando localmente que:

- Captura a imagem da câmera
- Realiza o reconhecimento da mão e dos gestos
- Calcula se o mouse deve mover ou clicar com um dos botões
- Executa as ações do mouse

A versão que chama a API funciona da seguinte forma:

### Cliente

- Captura a imagem da câmera
- Envia a imagem para a API
- Executa as ações do mouse, de acordo com a resposta da API

### API

- Recebe a imagem
- Realiza o reconhecimento da mão e dos gestos
- Calcula se o mouse deve mover ou clicar com um dos botões
- Envia a resposta para o cliente executar
