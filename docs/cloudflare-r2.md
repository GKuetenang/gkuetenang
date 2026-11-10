# Médias de production avec Cloudflare R2

Le stockage local reste le comportement par défaut. Cloudflare R2 est activé
uniquement lorsque `R2_ENABLED=true`. Cette configuration concerne les médias
publics du portfolio ; les fichiers statiques restent servis par WhiteNoise.

## Préparer Cloudflare

1. Créer un bucket R2 avec la classe de stockage **Standard**.
2. Relier un domaine personnalisé au bucket, par exemple
   `media.example.com`. Le sous-domaine `r2.dev` ne doit servir qu'aux essais.
3. Créer un jeton de compte avec la permission **Object Read & Write**, limité
   à ce bucket.
4. Conserver l'Access Key ID et la Secret Access Key dans le gestionnaire de
   secrets du déploiement. Ne jamais les versionner.

Les uploads de l'administration Django passent par le serveur. Aucun CORS
n'est nécessaire pour cet usage ni pour un simple affichage avec `<img>`.

## Variables de production

```dotenv
R2_ENABLED=true
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
R2_PUBLIC_HOSTNAME=media.example.com
```

`R2_ENDPOINT_URL` doit être l'endpoint S3 complet fourni par Cloudflare. Un
bucket juridictionnel utilise son endpoint spécifique. Le nom d'hôte public ne
doit contenir ni `https://`, ni chemin, ni slash final.

## Copier les images existantes

Pour une première installation sans projet ni média, ignorer entièrement cette
section : aucune sauvegarde et aucune commande de copie ne sont nécessaires.

Avant d'activer R2 sur le service web :

1. S'il existe déjà des données, sauvegarder la base et le volume Docker
   `media_data`. Ce volume est monté dans `/app/media` dans le conteneur web.
2. Appliquer la migration Django dans l'environnement de déploiement.
3. Lancer la simulation depuis un environnement qui possède à la fois le
   répertoire média local et les variables R2. Avec la configuration Docker
   actuelle :

   ```console
   docker compose run --rm --no-deps web \
     python manage.py migrate_project_images_to_r2
   ```

   Hors conteneur, utiliser `uv run --env-file .env python manage.py
   migrate_project_images_to_r2`.

4. Corriger toute source absente, puis exécuter la copie :

   ```console
   docker compose run --rm --no-deps web \
     python manage.py migrate_project_images_to_r2 --execute
   ```

La commande conserve les mêmes clés, ignore les objets déjà présents, ne
supprime jamais la source locale et renvoie une erreur si la copie est
incomplète. Elle peut donc être relancée.

5. Vérifier le nombre d'objets, plusieurs tailles et plusieurs URL publiques.
6. Recréer le service web avec `R2_ENABLED=true` seulement après ces contrôles.
7. Conserver la sauvegarde locale jusqu'à validation complète en production.

Pour revenir temporairement au stockage local, remettre `R2_ENABLED=false` et
redémarrer l'application tant que le répertoire média d'origine est conservé.

Ce bucket est public. Il ne doit pas recevoir de documents privés ni de
données personnelles nécessitant un contrôle d'accès.

## Références officielles

- [Cloudflare R2 — API compatible S3](https://developers.cloudflare.com/r2/get-started/s3/)
- [Cloudflare R2 — classes de stockage](https://developers.cloudflare.com/r2/buckets/storage-classes/)
- [Cloudflare R2 — buckets publics](https://developers.cloudflare.com/r2/buckets/public-buckets/)
- [django-storages 1.14.6 — backend S3](https://django-storages.readthedocs.io/en/1.14.6/backends/amazon-S3.html)
