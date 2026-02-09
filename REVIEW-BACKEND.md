# 🔍 Review Backend - Habit Tracker

**Date**: 2024-02-09  
**Reviewer**: Subagent Backend #1  
**Scope**: `/habit-tracker/backend/`

---

## 📊 Score Global: **7.5/10**

Le code est globalement bien structuré avec une bonne séparation des responsabilités. Quelques erreurs bloquantes ont été corrigées et des améliorations sont suggérées.

---

## ✅ Ce qui est bien fait

### Architecture
- **Séparation claire** entre models, schemas, routers, et services
- **Async/await** utilisé correctement avec SQLAlchemy 2.0
- **Pydantic v2** bien configuré avec `ConfigDict(from_attributes=True)`
- **FastAPI best practices** : dépendances typées, schemas de réponse explicites

### Modèles SQLAlchemy
- **Mixins réutilisables** (`UUIDMixin`, `TimestampMixin`) - DRY
- **Relations bien définies** avec `back_populates`
- **Index stratégiques** sur les colonnes fréquemment requêtées
- **Contraintes d'unicité** appropriées (email, username, friend_code)
- **Soft delete** implémenté proprement avec `deleted_at`

### Schemas Pydantic
- **Validation forte** avec `field_validator` pour passwords, usernames
- **Documentation riche** avec `Field(description=..., examples=[...])`
- **Enums bien utilisés** pour les types finis (Difficulty, Priority, etc.)

### Sécurité
- **JWT correctement implémenté** avec refresh tokens
- **Hachage bcrypt** via passlib
- **Protection contre l'énumération d'emails** dans forgot-password
- **GDPR compliance** : anonymisation des données à la suppression

### Services
- **Logique métier isolée** (xp_service, streak_service, level_service)
- **Formules de gamification documentées** dans les docstrings
- **LLM service** avec fallback et gestion d'erreurs robuste

### Celery Tasks
- **Retry logic** avec exponential backoff
- **Séparation claire** : llm_tasks, notification_tasks, stats_tasks, cleanup_tasks
- **Beat schedule** pour les tâches périodiques

---

## ⚠️ Avertissements (non bloquants)

### 1. Duplication de `get_db()`
**Fichiers**: `app/database.py` et `app/utils/dependencies.py`

Les deux définissent `get_db()` de manière quasi-identique. Risque de confusion.

**Recommandation**: Garder uniquement dans `app/database.py` et importer ailleurs.

### 2. Duplication des dépendances d'authentification
**Fichiers**: `app/deps.py` et `app/utils/dependencies.py`

Deux modules font la même chose avec des implémentations légèrement différentes.

**Recommandation**: Supprimer `app/deps.py` et utiliser uniquement `app/utils/dependencies.py`.

### 3. Incohérence de nommage model/schema
| Schema | Champ | Model | Champ |
|--------|-------|-------|-------|
| `HabitBase` | `title` | `Habit` | `name` |
| `HabitBase` | `base_xp` | `Habit` | ❌ (pas stocké) |
| `HabitBase` | `base_coins` | `Habit` | ❌ (pas stocké) |

Le mapping manuel dans `habit_to_response()` fonctionne mais crée de la confusion.

**Recommandation**: Aligner les noms ou documenter explicitement les mappings.

### 4. Schema `CharacterResponse` incomplet
Le schema a des champs non présents dans le modèle:
- `hp`, `max_hp` → Non définis dans `Character`
- `gems` → Non défini
- `current_xp`, `xp_to_next_level` → Calculés dynamiquement

**Impact**: La sérialisation échouera sans mapping manuel.

**Recommandation**: Ajouter les champs au modèle ou créer une méthode de conversion.

### 5. Services sync dans contexte async
**Fichiers**: `app/services/xp_service.py`, `app/services/streak_service.py`

Les services utilisent `Session` (sync) mais sont appelés depuis des endpoints async avec `# type: ignore`.

```python
add_xp(
    db=db,  # type: ignore - async session compatibility
    user=current_user,
    ...
)
```

**Impact**: Fonctionne grâce à asyncpg mais pas idéal.

**Recommandation**: Migrer les services vers async ou créer des wrappers explicites.

### 6. `lazy="selectin"` partout
Toutes les relations utilisent `lazy="selectin"` ce qui charge automatiquement les données liées.

**Impact**: Peut causer des requêtes N+1 sur des endpoints légers.

**Recommandation**: Utiliser `lazy="raise"` par défaut et charger explicitement avec `options(selectinload(...))`.

### 7. Pas de validation de rate limit pour LLM
**Fichier**: `app/models/stats.py`

Le modèle `RateLimit` existe mais n'est pas utilisé dans les endpoints de création de tâches.

**Recommandation**: Implémenter la vérification avant d'appeler `evaluate_task_difficulty`.

---

## ❌ Erreurs corrigées (étaient bloquantes)

### 1. ✅ CORRIGÉ - Imports manquants dans Celery tasks
**Fichiers**: 
- `app/tasks/__init__.py`
- `app/routers/tasks.py`

**Problème**: Import de `evaluate_task_difficulty` et `reevaluate_task` qui n'existaient pas.

**Correction appliquée**: Ajout des fonctions aliases dans `llm_tasks.py`:
```python
@shared_task(...)
def evaluate_task_difficulty(self, task_id: str):
    """Alias for evaluate_task_async"""
    ...

@shared_task(...)
def reevaluate_task(self, task_id: str):
    """Re-evaluate an existing task."""
    ...
```

### 2. ✅ CORRIGÉ - Import `timedelta` mal placé
**Fichier**: `app/routers/habits.py`

**Problème**: `from datetime import timedelta` était à la fin du fichier (ligne 406) alors qu'utilisé avant.

**Correction appliquée**: Déplacé dans les imports en haut du fichier.

### 3. ✅ CORRIGÉ - Propriété `is_active` manquante
**Fichier**: `app/schemas/user.py` / `app/models/user.py`

**Problème**: `UserResponse` avait `is_active: bool` mais le modèle `User` n'avait pas cet attribut.

**Correction appliquée**: Ajout d'une propriété dérivée dans le modèle:
```python
@property
def is_active(self) -> bool:
    """Check if user account is active (not deleted)."""
    return self.deleted_at is None
```

---

## 📋 Vérifications effectuées

| Check | Résultat |
|-------|----------|
| Syntaxe Python (65 fichiers) | ✅ OK |
| Imports circulaires | ✅ Aucun détecté |
| Relations SQLAlchemy | ✅ Cohérentes |
| Schemas Pydantic | ⚠️ Quelques incohérences |
| Dépendances d'auth | ✅ Correctes |
| Sessions DB | ⚠️ Mixte sync/async |
| Routers response models | ✅ Corrects |

---

## 🎯 Recommandations prioritaires

1. **Supprimer `app/deps.py`** - Utiliser uniquement `app/utils/dependencies.py`
2. **Unifier `get_db()`** - Un seul endroit
3. **Ajouter rate limiting** - Avant les appels LLM
4. **Compléter `CharacterResponse`** - Ajouter les champs manquants au modèle ou créer une factory
5. **Tests d'intégration** - Ajouter des tests pour les endpoints critiques (auth, completions)

---

## 📁 Fichiers modifiés

```
app/tasks/llm_tasks.py      # Ajout de evaluate_task_difficulty et reevaluate_task
app/routers/habits.py       # Déplacement de l'import timedelta
app/models/user.py          # Ajout de la propriété is_active
```

---

*Review effectuée par Shiro (Subagent Backend #1)*
