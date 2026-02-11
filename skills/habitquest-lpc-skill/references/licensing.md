# Guide de Licensing et Crédits LPC

L'utilisation de sprites LPC est soumise à des obligations de crédits. Ce guide
explique comment s'y conformer correctement.

## Licences supportées

Les assets LPC sont distribués sous une ou plusieurs de ces licences :

| Licence | Attribution | DRM OK ? | Dérivés |
|---------|------------|----------|---------|
| CC0 | Non requise | Oui | Libre |
| CC-BY-SA 3.0+ | Obligatoire | Flou (prudence) | Sous CC-BY-SA |
| CC-BY 4.0 | Obligatoire | Flou (prudence) | Libre |
| OGA-BY 3.0 | Obligatoire | Oui | Libre |
| GPL 3.0 | Obligatoire | Oui | Sous GPL |

**CC-BY-SA 3.0 est la licence la plus restrictive** et couvre la majorité des assets.
En la respectant, on couvre tous les cas.

## Obligations concrètes

Pour tout projet utilisant des sprites LPC, il faut :

1. **Créditer les auteurs** — liste de tous les contributeurs dont les assets sont utilisés
2. **Indiquer la licence** — mentionner CC-BY-SA 3.0 et GPL 3.0
3. **Lien vers la source** — lien vers OpenGameArt.org ou le repo GitHub
4. **Rendre les crédits accessibles** — visible dans l'interface (page crédits, footer, etc.)

## Template de crédits (à inclure TOUJOURS)

### Version courte (commentaire HTML)
```html
<!--
  Character sprites from the Liberated Pixel Cup (LPC) project.
  Generated with: https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator/
  
  Artists: Stephen Challener (Redshrike), Johannes Sjölund (wulax),
  Matthew Krohn (makrohn), Lanea Zimmerman (Sharm), bluecarrot16,
  Benjamin K. Smith (BenCreating), Eliza Wyatt (ElizaWy),
  and many other contributors.
  
  Full credits: https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator/blob/master/CREDITS.csv
  
  Licenses:
  - CC-BY-SA 3.0: https://creativecommons.org/licenses/by-sa/3.0/
  - GPL 3.0: https://www.gnu.org/licenses/gpl-3.0.html
  
  LPC Collection: https://opengameart.org/content/lpc-collection
-->
```

### Version visible (footer ou page crédits)
```html
<footer class="lpc-credits">
  <p>
    Character sprites from the
    <a href="https://opengameart.org/content/lpc-collection">Liberated Pixel Cup</a> project.
    Created with the
    <a href="https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator/">
      Universal LPC Spritesheet Generator
    </a>.
  </p>
  <p>
    Licensed under
    <a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA 3.0</a> /
    <a href="https://www.gnu.org/licenses/gpl-3.0.html">GPL 3.0</a>.
    <a href="https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator/blob/master/CREDITS.csv">
      Full credits
    </a>.
  </p>
</footer>
```

## Comment obtenir les crédits exacts

Le générateur en ligne propose un bouton de téléchargement des crédits (CSV ou texte)
correspondant exactement aux assets sélectionnés. Recommander à l'utilisateur de :

1. Aller sur le générateur : https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator/
2. Configurer le personnage
3. Télécharger le PNG ET le fichier de crédits
4. Intégrer les crédits dans le projet

## Note pour les projets commerciaux

L'utilisation dans des projets commerciaux est autorisée, mais sous conditions :
- Attribution obligatoire
- Les dérivés doivent être sous la même licence (CC-BY-SA / GPL)
- Attention au DRM : CC-BY-SA interdit potentiellement le chiffrement DRM
  (prudence pour Steam, App Store). Utiliser des assets CC0 ou OGA-BY si nécessaire.
