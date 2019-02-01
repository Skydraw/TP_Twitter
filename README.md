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
