# Social APIs Setup Guide

## 1. Objetivo

Este documento descreve o passo a passo de configuração das APIs necessárias para publicar vídeos e thumbnails em:

- YouTube
- Instagram
- Facebook

Ele foi escrito para apoiar a implementação do sistema e o onboarding operacional da equipe.

## 2. Observações importantes

1. Telas e nomes no painel do Google e da Meta podem mudar com o tempo.
2. Em produção, permissões sensíveis normalmente exigem revisão de app e, em alguns casos, verificação de negócio.
3. O sistema deve armazenar segredos apenas em variáveis de ambiente ou cofre de segredos.
4. Para Instagram e Facebook, o fluxo suportado depende do tipo de conta, página e permissões aprovadas.

## 3. YouTube

### 3.1 Pré-requisitos

- Conta Google com acesso ao canal do YouTube que fará upload
- Projeto no Google Cloud
- OAuth consent configurado
- YouTube Data API v3 ativada

### 3.2 Passo a passo

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2. Crie um novo projeto ou selecione um projeto existente.
3. Em `APIs & Services`, ative a `YouTube Data API v3`.
4. Configure a `OAuth consent screen`.
5. Crie credenciais `OAuth 2.0 Client ID` para o tipo de aplicação que seu backend usará.
6. Configure os redirect URIs necessários para o fluxo OAuth.
7. Solicite ao menos o escopo de upload compatível com o fluxo:
   - `https://www.googleapis.com/auth/youtube.upload`
8. Implemente o fluxo OAuth para obter e renovar tokens de acesso.
9. Para upload de vídeo, use `videos.insert`.
10. Para thumbnail customizada, use `thumbnails.set`.

### 3.3 Pontos de atenção

- Projetos não verificados podem ter uploads restritos a `private` por padrão.
- Upload de vídeo consome quota alta.
- Thumbnail customizada exige permissões adequadas no canal.

### 3.4 Links oficiais

- [YouTube Data API overview](https://developers.google.com/youtube/v3)
- [Upload a Video guide](https://developers.google.com/youtube/v3/guides/uploading_a_video)
- [videos.insert reference](https://developers.google.com/youtube/v3/docs/videos/insert)
- [thumbnails.set reference](https://developers.google.com/youtube/v3/docs/thumbnails/set)

## 4. Instagram

### 4.1 Pré-requisitos

- Conta Meta Developer
- App Meta configurado
- Conta Instagram profissional compatível com a API suportada
- Em muitos cenários, conta Instagram conectada a uma Facebook Page
- Permissões aprovadas para leitura/publicação conforme o fluxo adotado

### 4.2 Passo a passo geral

1. Acesse o [Meta for Developers](https://developers.facebook.com/).
2. Crie um app apropriado para uso de negócio.
3. Adicione os produtos necessários do ecossistema Meta para o fluxo escolhido.
4. Garanta que a conta do Instagram seja `Business` ou `Creator`, conforme o suporte atual da API usada pelo app.
5. Se o fluxo adotado depender de Page, conecte a conta do Instagram à Facebook Page correta.
6. Configure login/autorização para obter user access token com as permissões exigidas.
7. Confirme acesso ao identificador da conta Instagram a partir da conta/página conectada.
8. Para publicar mídia, siga o fluxo de duas etapas:
   - criar container de mídia
   - publicar o container
9. Registre e trate limites, status assíncronos e falhas de publicação.

### 4.3 Permissões e validações que normalmente entram no fluxo

Dependendo do cenário, valide pelo menos as permissões equivalentes a:

- leitura básica da conta Instagram profissional
- publicação de conteúdo no Instagram
- leitura/listagem da Page conectada, quando o fluxo passa por Page

### 4.4 Pontos de atenção

- O suporte de publicação depende do tipo de conta e do recurso suportado pela API.
- Nem todo formato social tem o mesmo fluxo ou as mesmas limitações.
- Em produção, permissões de publicação podem exigir App Review e Business Verification.

### 4.5 Links oficiais

- [Instagram API overview](https://developers.facebook.com/docs/instagram-api/overview)
- [Instagram content publishing guide](https://developers.facebook.com/docs/instagram-api/guides/content-publishing)
- [Instagram media publish reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media_publish)

## 5. Facebook

### 5.1 Pré-requisitos

- Conta Meta Developer
- App Meta configurado
- Facebook Page sob administração da conta autorizadora
- Permissões aprovadas para operar em Pages

### 5.2 Passo a passo geral

1. Acesse o [Meta for Developers](https://developers.facebook.com/).
2. Use ou crie um app compatível com publicação em Pages.
3. Configure o fluxo de autenticação para obter user access token com permissões de Page.
4. Recupere a lista de Pages às quais o usuário tem acesso.
5. Obtenha o Page access token correspondente.
6. Para publicação de vídeo, implemente o fluxo suportado pela Video API / Graph API para upload ou publicação por URL, conforme o caso suportado.
7. Persista `page_id`, token de operação e resposta da plataforma.
8. Trate processamento assíncrono e status finais.

### 5.3 Permissões e validações que normalmente entram no fluxo

Valide pelo menos as permissões equivalentes a:

- listar páginas acessíveis
- publicar posts/conteúdo em Pages
- recursos extras conforme webhooks, insights ou gestão ampliada

### 5.4 Pontos de atenção

- Publicação em Page exige token correto do tipo Page.
- Vídeo pode ter processamento assíncrono depois do upload.
- Em produção, permissões para Pages normalmente exigem App Review.

### 5.5 Links oficiais

- [Graph API overview](https://developers.facebook.com/docs/graph-api)
- [Pages permissions and features overview](https://developers.facebook.com/docs/pages/overview/permissions-features)
- [Video API publishing guide](https://developers.facebook.com/docs/video-api/guides/publishing)

## 6. Variáveis de ambiente recomendadas

### YouTube

- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REDIRECT_URI`
- `YOUTUBE_REFRESH_TOKEN`

### Meta / Instagram / Facebook

- `META_APP_ID`
- `META_APP_SECRET`
- `META_REDIRECT_URI`
- `META_USER_ACCESS_TOKEN`
- `META_PAGE_ACCESS_TOKEN`

### Internas do sistema

- `SOCIAL_PUBLISHING_ENABLED`
- `DEFAULT_YOUTUBE_CHANNEL_ID`
- `DEFAULT_FACEBOOK_PAGE_ID`
- `DEFAULT_INSTAGRAM_ACCOUNT_ID`

## 7. Recomendação de implementação

### Ordem sugerida

1. Fechar persistência e auditabilidade dos publish attempts.
2. Implementar YouTube primeiro.
3. Implementar Facebook Pages depois.
4. Implementar Instagram com o fluxo de publicação suportado para a conta-alvo.
5. Acoplar geração de thumbnail ao publish pipeline.

### Estratégia de segurança

1. Nunca guardar tokens em banco sem criptografia ou estratégia clara de segredo.
2. Separar credenciais por organização/publicação quando o produto evoluir para operação multi-tenant.
3. Persistir logs de tentativa, resposta, erro e external IDs.

## 8. Observação final

Para Meta, é essencial revisar no momento da implementação:

- se o tipo de app escolhido continua compatível
- se as permissões exatas exigidas pelo fluxo continuam as mesmas
- se o tipo de conta Instagram/Page alvo suporta o formato desejado

Isso é importante porque a plataforma Meta altera fluxos e nomenclaturas com mais frequência do que o contrato interno do nosso sistema.
