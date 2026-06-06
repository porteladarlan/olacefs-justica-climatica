# Comandos pós-deploy para o ambiente de teste

## 1. Rodar migrações

```bash
python manage.py migrate
```

## 2. Coletar arquivos estáticos

```bash
python manage.py collectstatic --noinput
```

## 3. Carregar dados demonstrativos

```bash
python manage.py carregar_dados_ficticios --limpar-demo
```

## 4. Criar superusuário ou usuário staff

```bash
python manage.py createsuperuser
```

## 5. Conferir auditorias localmente antes de enviar o link

```powershell
python manage.py test
python manage.py auditar_traducoes_trilingues
python manage.py auditar_autenticacao_perfis
python manage.py validar_fluxo_ponta_a_ponta
python manage.py checar_prontidao_ambiente
python manage.py validar_entrega_final
```

## 6. Conferir dados demonstrativos

Acessar:

- `/catalogo/`
- `/en/catalogo/`
- `/es/catalogo/`

## 7. Conferir login/cadastro

Acessar:

- `/cadastro/`
- `/entrar/`
- `/adicionar-boa-pratica/`
