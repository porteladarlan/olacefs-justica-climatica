# Fase 16A — Checklist de preparação do Render para teste externo

## Objetivo

Preparar o ambiente Render/teste externo para disponibilizar a plataforma às pessoas testadoras com segurança mínima, dados demonstrativos e validações básicas.

## Antes do deploy

Confirmar localmente:

```powershell
git checkout main
git pull origin main
python manage.py test
python manage.py auditar_traducoes_trilingues
python manage.py auditar_autenticacao_perfis
python manage.py validar_fluxo_ponta_a_ponta
python manage.py checar_prontidao_ambiente
python manage.py validar_release_validacao
```

## Conferir no GitHub

- [ ] PR final mergeada na `main`.
- [ ] GitHub Actions verde.
- [ ] Tag da versão criada, se aplicável.
- [ ] Branch de teste externo alinhada com `main`.

## Variáveis no Render

Conferir no painel do Render:

- [ ] `SECRET_KEY`
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS`
- [ ] `CSRF_TRUSTED_ORIGINS`
- [ ] configuração de banco, se houver
- [ ] configuração de arquivos/anexos, se houver
- [ ] comando de build
- [ ] comando de start

## Comandos esperados no ambiente

Após deploy:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py carregar_dados_ficticios --limpar-demo
```

## Validação manual da URL pública

Validar:

- [ ] `/`
- [ ] `/catalogo/`
- [ ] `/banco-tecnico/`
- [ ] `/normas-internacionais/`
- [ ] `/sobre/`
- [ ] `/cadastro/`
- [ ] `/entrar/`
- [ ] `/adicionar-boa-pratica/`
- [ ] `/meus-envios/`
- [ ] `/painel-revisao/`
- [ ] `/painel-revisao-edicoes/`
- [ ] `/en/`
- [ ] `/es/`

## Limitações a comunicar

- possível lentidão na primeira abertura;
- possível reinicialização do serviço;
- persistência de arquivos depende da configuração;
- banco pode ser temporário se não houver banco externo;
- dados demonstrativos podem ser recarregados;
- não é ambiente de produção final.
