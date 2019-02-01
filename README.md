# TP Twitter

**Partie Golang**

 - Installer MySQL & Golang > 1.10
 - Importer le fichier SQL
 - go run main.go

**Soucis côté golang**

# [checkbox:checked] Potentiel injection SQL dans la saisie d'un tweet : *patché*
```go
_, err := stmt.Exec(id, html.EscapeString(tweet))
```
