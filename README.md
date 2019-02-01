# TP Twitter

**Partie Golang**

 - Installer MySQL & Golang > 1.10
 - Importer le fichier SQL
 - go run main.go

**Soucis côté golang**

[X] Potentiel injection SQL dans la saisie d'un tweet : Patch de toutes les entrées utilisateurs avec html.EscapeString
```go
_, err := stmt.Exec(id, html.EscapeString(tweet))
```

**Partie Python**  
[X] Injection SQL dans la requête user?id=1 : *patché*
```python
try:
 i = int(UserID)
  ...
else:
 return None
```



**Injection XSS**

[X] XSS dans le champs tweet  

```javascript
<script>document.write(document.cookie)</script>
```
**Reutilisation de cookies utilisateurs**

1: Récupération du cookie de l'utilisateurN.

2: Création de tweet avec utilisateurX

3: Avec burp incrementation du cookie de l'utilisateur N dans la requete de création de tweet de l'utilisateurX

4: Poste du tweet avec la session de l'utilisateurN



