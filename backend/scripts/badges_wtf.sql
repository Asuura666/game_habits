-- 🐺 Badges WTF/Drôles pour HabitQuest
-- Par Kuro - 2026-02-12

INSERT INTO badges (id, code, name, description, icon, rarity, xp_reward, condition_type, condition_value, is_secret, is_seasonal) VALUES

-- === COMMON (25 XP) - Les classiques décalés ===
(gen_random_uuid(), 'procrastinator_repenti', 'Procrastinateur Repenti', 'Compléter une habitude après 23h. Mieux vaut tard que jamais !', '🦥', 'common', 25, 'time_based', '{"after_hour": 23}', false, false),
(gen_random_uuid(), 'lundi_deteste', 'Lundi Détesté', 'Compléter 10 habitudes un lundi. Le lundi te déteste aussi.', '😩', 'common', 25, 'day_completions', '{"day": "monday", "count": 10}', false, false),
(gen_random_uuid(), 'vendredi_libre', 'Vendredi Libéré', 'Terminer toutes ses habitudes avant 18h un vendredi. WEEKEND !', '🎉', 'common', 25, 'day_completions', '{"day": "friday", "before_hour": 18}', false, false),
(gen_random_uuid(), 'snooze_master', 'Snooze Master', 'Compléter une habitude matinale après 11h. Le snooze a gagné.', '😴', 'common', 25, 'time_based', '{"category": "morning", "after_hour": 11}', false, false),
(gen_random_uuid(), 'debutant_chanceux', 'Débutant Chanceux', 'Gagner plus de 50 coins en une journée dès la première semaine.', '🍀', 'common', 25, 'coins_earned', '{"daily_min": 50, "within_days": 7}', false, false),
(gen_random_uuid(), 'clickeur_fou', 'Clickeur Fou', 'Compléter 5 habitudes en moins de 2 minutes. Speed run !', '⚡', 'common', 25, 'speed_completion', '{"count": 5, "minutes": 2}', false, false),
(gen_random_uuid(), 'minimalist', 'Minimaliste', 'Avoir exactement 1 habitude active pendant 7 jours. Less is more.', '🧘', 'common', 25, 'habits_count', '{"exact": 1, "days": 7}', false, false),
(gen_random_uuid(), 'maximalist', 'Maximaliste', 'Avoir 20+ habitudes actives en même temps. Tu aimes souffrir ?', '🤯', 'common', 25, 'habits_count', '{"min": 20}', false, false),

-- === UNCOMMON (50 XP) - Plus corsé ===
(gen_random_uuid(), 'insomniaque_productif', 'Insomniaque Productif', 'Compléter 5 habitudes entre 2h et 5h du matin. Dors-tu parfois ?', '🌙', 'uncommon', 50, 'time_based', '{"hour_range": [2, 5], "count": 5}', false, false),
(gen_random_uuid(), 'weekend_warrior', 'Weekend Warrior', 'Maintenir un streak parfait pendant tout un weekend.', '⚔️', 'uncommon', 50, 'perfect_period', '{"type": "weekend", "count": 1}', false, false),
(gen_random_uuid(), 'dieu_du_cafe', 'Dieu du Café', 'Compléter 100 habitudes avec le tag "morning".', '☕', 'uncommon', 50, 'category_completions', '{"category": "morning", "count": 100}', false, false),
(gen_random_uuid(), 'touch_grass', 'Touch Grass', 'Compléter 50 habitudes outdoor. Tu as vu le soleil !', '🌿', 'uncommon', 50, 'category_completions', '{"category": "outdoor", "count": 50}', false, false),
(gen_random_uuid(), 'no_life', 'No Life', 'Se connecter 30 jours consécutifs. As-tu des amis IRL ?', '🎮', 'uncommon', 50, 'active_days', '{"consecutive": 30}', false, false),
(gen_random_uuid(), 'drama_queen', 'Drama Queen', 'Briser un streak de 7+ jours, puis le reconstruire.', '👑', 'uncommon', 50, 'streak_recovery', '{"broken_min": 7, "recovered": true}', false, false),
(gen_random_uuid(), 'indecis', 'L''Indécis', 'Créer puis supprimer 5 habitudes. Tu sais ce que tu veux ?', '🤔', 'uncommon', 50, 'habits_deleted', '{"count": 5}', false, false),
(gen_random_uuid(), 'speedrunner', 'Speedrunner', 'Atteindre le niveau 10 en moins de 2 semaines.', '🏃', 'uncommon', 50, 'level_reached', '{"level": 10, "within_days": 14}', false, false),
(gen_random_uuid(), 'freezer_addict', 'Freezer Addict', 'Utiliser 5 streak freezes en un mois. Stratège ou feignant ?', '🥶', 'uncommon', 50, 'freezes_used', '{"count": 5, "period": "month"}', false, false),
(gen_random_uuid(), 'comeback_kid', 'Comeback Kid', 'Revenir après 7 jours d''inactivité et compléter une habitude.', '💪', 'uncommon', 50, 'inactivity_return', '{"days_inactive": 7}', false, false),
(gen_random_uuid(), 'patron', 'Le Patron', 'Avoir dépensé 1000 coins dans la boutique. L''économie te remercie.', '💸', 'uncommon', 50, 'coins_spent', '{"total": 1000}', false, false),

-- === RARE (100 XP) - Respect ===
(gen_random_uuid(), 'vampire', 'Vampire', 'Compléter 50 habitudes entre minuit et 6h. La lumière te brûle.', '🧛', 'rare', 100, 'time_based', '{"hour_range": [0, 6], "count": 50}', false, false),
(gen_random_uuid(), 'robot', 'Robot', 'Compléter ses habitudes à la même heure (±15min) pendant 14 jours.', '🤖', 'rare', 100, 'consistency', '{"variance_minutes": 15, "days": 14}', false, false),
(gen_random_uuid(), 'phoenix', 'Phoenix', 'Reconstruire un streak de 30 jours après l''avoir perdu.', '🔥', 'rare', 100, 'streak_recovery', '{"broken_min": 30, "recovered_min": 30}', false, false),
(gen_random_uuid(), 'grind_never_stops', 'Grind Never Stops', 'Compléter au moins 1 habitude chaque jour pendant 60 jours.', '💎', 'rare', 100, 'active_days', '{"consecutive": 60}', false, false),
(gen_random_uuid(), 'fashionista_supreme', 'Fashionista Suprême', 'Posséder 30 items différents. Tu collectionnes les pixels ?', '👗', 'rare', 100, 'items_owned', '{"count": 30}', false, false),
(gen_random_uuid(), 'social_butterfly', 'Social Butterfly', 'Avoir 20 amis actifs. T''es populaire ou quoi ?', '🦋', 'rare', 100, 'friends_count', '{"active": 20}', false, false),
(gen_random_uuid(), 'tryhard', 'Tryhard', 'Compléter plus de 100 habitudes en une semaine. Respire un peu.', '😤', 'rare', 100, 'weekly_completions', '{"count": 100}', false, false),
(gen_random_uuid(), 'all_rounder', 'All-Rounder', 'Avoir des habitudes dans 10 catégories différentes.', '🎯', 'rare', 100, 'categories_count', '{"count": 10}', false, false),

-- === EPIC (200 XP) - Légende en devenir ===
(gen_random_uuid(), 'masochiste', 'Le Masochiste', 'Maintenir 30 habitudes actives avec un streak de 30+ jours.', '💀', 'epic', 200, 'habits_count', '{"min": 30, "all_streak_min": 30}', false, false),
(gen_random_uuid(), 'perfectionist', 'Perfectionniste Absolu', 'Compléter 100% de ses habitudes pendant 90 jours consécutifs.', '✨', 'epic', 200, 'perfect_period', '{"days": 90}', false, false),
(gen_random_uuid(), 'time_traveler', 'Time Traveler', 'Utiliser le backfill pour corriger 30 jours passés. L''histoire se réécrit.', '⏰', 'epic', 200, 'backfills_used', '{"count": 30}', false, false),
(gen_random_uuid(), 'whale', 'Baleine', 'Dépenser 10000 coins dans la boutique. Le jeu te remercie.', '🐋', 'epic', 200, 'coins_spent', '{"total": 10000}', false, false),
(gen_random_uuid(), 'mentor', 'Mentor', 'Avoir 5 amis qui ont atteint le niveau 10 après t''avoir ajouté.', '🎓', 'epic', 200, 'friends_leveled', '{"count": 5, "level": 10}', false, false),

-- === LEGENDARY (500 XP) - Mythique ===
(gen_random_uuid(), 'elu', 'L''Élu', 'Être dans le top 1% des joueurs. Tu es différent.', '👁️', 'legendary', 500, 'leaderboard_percentile', '{"top": 1}', false, false),
(gen_random_uuid(), 'no_life_supreme', 'No Life Suprême', 'Se connecter 365 jours consécutifs. Une année complète. Wow.', '🏆', 'legendary', 500, 'active_days', '{"consecutive": 365}', false, false),
(gen_random_uuid(), 'immortal_grind', 'Immortal Grind', 'Compléter 10000 habitudes au total. Tu as transcendé.', '⚡', 'legendary', 500, 'total_completions', '{"count": 10000}', false, false),
(gen_random_uuid(), 'founder', 'OG Founder', 'Avoir créé son compte dans les 30 premiers jours du lancement.', '🏅', 'legendary', 500, 'account_age', '{"early_adopter_days": 30}', true, false),

-- === SECRET BADGES (cachés jusqu'à obtention) ===
(gen_random_uuid(), 'oops', 'Oops', 'Supprimer une habitude avec un streak de 50+ jours. Ça fait mal.', '😱', 'rare', 100, 'habit_deleted', '{"streak_min": 50}', true, false),
(gen_random_uuid(), 'easter_egg', 'Easter Egg', 'Trouver l''easter egg caché dans l''app.', '🥚', 'epic', 200, 'special', '{"type": "easter_egg"}', true, false),
(gen_random_uuid(), 'bug_hunter', 'Bug Hunter', 'Reporter un bug valide à l''équipe. Merci !', '🐛', 'rare', 100, 'special', '{"type": "bug_report"}', true, false),
(gen_random_uuid(), 'rickrolled', 'Rickrolled', 'Cliquer sur un lien suspect dans les notes d''une habitude.', '🎵', 'uncommon', 50, 'special', '{"type": "rickroll"}', true, false),
(gen_random_uuid(), 'nice', 'Nice', 'Avoir exactement 69 completions ou 420 XP total. Nice.', '😏', 'uncommon', 50, 'special', '{"values": [69, 420]}', true, false),

-- === SEASONAL (événements spéciaux) ===
(gen_random_uuid(), 'resolution_keeper', 'Gardien des Résolutions', 'Tenir une habitude créée le 1er janvier pendant tout janvier.', '🎆', 'rare', 100, 'new_year', '{"created": "01-01", "kept_days": 31}', false, true),
(gen_random_uuid(), 'halloween_grind', 'Halloween Grind', 'Compléter 31 habitudes le 31 octobre. Spooky productivity.', '🎃', 'uncommon', 50, 'holiday', '{"date": "10-31", "count": 31}', false, true),
(gen_random_uuid(), 'xmas_miracle', 'Miracle de Noël', 'Maintenir son streak le 25 décembre. Même le Père Noël grind.', '🎄', 'uncommon', 50, 'holiday', '{"date": "12-25"}', false, true),
(gen_random_uuid(), 'friday_13', 'Vendredi 13', 'Avoir un streak de 13 jours qui inclut un vendredi 13.', '🖤', 'rare', 100, 'special_date', '{"type": "friday_13", "streak": 13}', true, true)

ON CONFLICT (code) DO NOTHING;
