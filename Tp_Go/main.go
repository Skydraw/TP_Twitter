package main

import (
	"database/sql"
	"fmt"
	"html"
	"html/template"
	"log"
	"net/http"

	"golang.org/x/crypto/bcrypt"

	_ "github.com/go-sql-driver/mysql"
	"github.com/kataras/go-sessions"
)

var db *sql.DB
var err error

type user struct {
	ID        int
	Username  string
	FirstName string
	LastName  string
	Password  string
}

func connectDB() {
	db, err = sql.Open("mysql", "go:mypassword@tcp(127.0.0.1)/go_db")

	if err != nil {
		log.Fatalln(err)
	}

	err = db.Ping()
	if err != nil {
		log.Fatalln(err)
	}
}

func routes() {
	http.HandleFunc("/", home)
	http.HandleFunc("/register", register)
	http.HandleFunc("/login", login)
	http.HandleFunc("/wrongLogins", wrongLogins)
	http.HandleFunc("/logout", logout)
	http.HandleFunc("/users", listUsers)
	http.HandleFunc("/tweets", listTweets)
	http.HandleFunc("/newTweet", newTweet)
	http.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))
}

func main() {
	connectDB()
	routes()

	defer db.Close()

	fmt.Println("Server running on port :8100")
	http.ListenAndServe(":8100", nil)
}

func checkErr(w http.ResponseWriter, r *http.Request, err error) bool {
	if err != nil {
		http.Redirect(w, r, r.Host+r.URL.Path, 301)
		return false
	}

	return true
}

func queryUser(username string) user {
	var users = user{}
	err = db.QueryRow(`
		SELECT id, 
		username, 
		first_name, 
		last_name, 
		password 
		FROM users WHERE username=?
		`, username).
		Scan(
			&users.ID,
			&users.Username,
			&users.FirstName,
			&users.LastName,
			&users.Password,
		)
	return users
}

func home(w http.ResponseWriter, r *http.Request) {
	session := sessions.Start(w, r)
	if len(session.GetString("username")) == 0 {
		http.Redirect(w, r, "/login", 301)
	}

	var data = map[string]string{
		"username": session.GetString("username"),
		"message":  "Welcome to the Go !",
	}
	var t, err = template.ParseFiles("views/home.html")
	if err != nil {
		fmt.Println(err.Error())
		return
	}
	t.Execute(w, data)

	return
}

func newTweet(w http.ResponseWriter, r *http.Request) {
	var id int

	session := sessions.Start(w, r)
	if len(session.GetString("username")) == 0 {
		http.Redirect(w, r, "/login", 301)
	}

	if r.Method != "POST" {
		http.ServeFile(w, r, "views/home.html")
		return
	}

	tweet := r.FormValue("tweet")
	username := session.GetString("username")

	userID, err := db.Query("SELECT id FROM users WHERE username = ?", username)

	if err == nil {
		for userID.Next() {
			err = userID.Scan(&id)
		}
	}
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	stmt, err := db.Prepare("INSERT INTO tweets SET userID=?, tweet=?")
	if err == nil {
		_, err := stmt.Exec(id, html.EscapeString(tweet))
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
	}

	http.Redirect(w, r, "/home", http.StatusSeeOther)
	return
}

func register(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.ServeFile(w, r, "views/register.html")
		return
	}

	username := r.FormValue("username")
	firstName := r.FormValue("first_name")
	lastName := r.FormValue("last_name")
	password := r.FormValue("password")

	users := queryUser(username)

	if (user{}) == users {
		hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)

		if len(hashedPassword) != 0 && checkErr(w, r, err) {
			stmt, err := db.Prepare("INSERT INTO users SET username=?, password=?, first_name=?, last_name=?")
			if err == nil {
				_, err := stmt.Exec(&username, &hashedPassword, &firstName, &lastName)
				if err != nil {
					http.Error(w, err.Error(), http.StatusInternalServerError)
					return
				}

				http.Redirect(w, r, "/login", http.StatusSeeOther)
				return
			}
		}
	} else {
		http.Redirect(w, r, "/register", 302)
	}
}

func login(w http.ResponseWriter, r *http.Request) {
	session := sessions.Start(w, r)
	if len(session.GetString("username")) != 0 && checkErr(w, r, err) {
		http.Redirect(w, r, "/", 302)
	}
	if r.Method != "POST" {
		http.ServeFile(w, r, "views/login.html")
		return
	}
	username := r.FormValue("username")
	password := r.FormValue("password")

	users := queryUser(username)

	var passwordTest = bcrypt.CompareHashAndPassword([]byte(users.Password), []byte(password))

	if passwordTest == nil {
		session := sessions.Start(w, r)
		session.Set("username", users.Username)
		session.Set("name", users.FirstName)
		http.Redirect(w, r, "/", 302)
	} else {
		http.Redirect(w, r, "/wrongLogins", 302)
		//http.Redirect(w, r, "/login", 302)
	}

}

func listUsers(w http.ResponseWriter, r *http.Request) {
	var username string
	var user []string

	userID, err := db.Query("SELECT username FROM users")

	if err == nil {
		for userID.Next() {
			err = userID.Scan(&username)
			user = append(user, username)
		}
		t, _ := template.ParseFiles("views/users.html")
		t.Execute(w, &user)
	}
}

func listTweets(w http.ResponseWriter, r *http.Request) {
	users, _ := r.URL.Query()["user"]
	var id int
	var tweet string
	var userTweet []string

	userID, err := db.Query("SELECT id FROM users WHERE username = ?", users[0])

	if err == nil {
		for userID.Next() {
			err = userID.Scan(&id)
		}
	}
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	tweets, err := db.Query("SELECT tweet FROM tweets where userID = ?", id)
	if err == nil {
		for tweets.Next() {
			err = tweets.Scan(&tweet)
			userTweet = append(userTweet, tweet)
		}

		t, _ := template.ParseFiles("views/tweets.html")
		t.Execute(w, &userTweet)
	}
	return

}

func wrongLogins(w http.ResponseWriter, r *http.Request) {
	http.ServeFile(w, r, "views/wrongLogins.html")
	return
}

func logout(w http.ResponseWriter, r *http.Request) {
	session := sessions.Start(w, r)
	session.Clear()
	sessions.Destroy(w, r)
	http.Redirect(w, r, "/", 302)
}
