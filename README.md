# acr-cpp-method-required-prefix

Arquivo config.json

## Atributos

- rules
  - prefix
    - String referente a qual prefixo deve possuir, obrigatorio
    - Obrigatorio
  - regexFile
    - Regex para saber se verifica ou não um arquivo, obrigatorio
    - Obrigatorio
  - comment
    - Comentario que deve ser adicionado, podendo possuir as variaveis do nome do method, path do arquivo e linha
    - Obrigatorio
  - accessFilter
    - Lista de modificadores de acesso que devem ser verificados
    - Não é obrigatorio
  - methodIgnore
    - Methods que devem ser ignorado, ou seja não precisam ter o prefixo configurado
    - Não é obrigatorio

```json
{
    "stage": "static",
    "rules": [
        {
            "prefix": "",
            "regexFile": "",
            "comment": "${METHOD_NAME} - ${FILE_PATH} - ${LINE}",
            "accessFilter": [],
            "methodIgnore": []
        }
    ]
}
```
