# Checklist pré-prod

## Backend
- [ ] Tous les endpoints critiques testés
- [ ] Alembic fonctionne proprement
- [ ] Aucun `create_all` restant
- [ ] Variables d'environnement centralisées
- [ ] Logs backend lisibles
- [ ] Notifications non bloquantes

## Frontend
- [ ] Pages principales branchées à l'API
- [ ] Aucun accès DB direct restant
- [ ] Aucune logique métier critique restant dans le front
- [ ] Gestion d'erreur API propre

## Données
- [ ] Schéma prêt PostgreSQL
- [ ] Script de migration SQLite -> PostgreSQL planifié
- [ ] Référentiels validés

## Qualité
- [ ] CI verte
- [ ] Tests backend passent
- [ ] Lint passe
- [ ] Parcours critiques testés manuellement

## Sécurité
- [ ] Secrets hors du code
- [ ] Rôles backend cohérents
- [ ] Préparation SSO cadrée

## Déploiement
- [ ] Dockerfiles valides
- [ ] docker-compose prêt
- [ ] Workflow staging présent
- [ ] Workflow prod présent