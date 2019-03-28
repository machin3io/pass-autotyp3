# pass-autotyp3

Rewrite of [wosc/pass-autotype](https://github.com/wosc/pass-autotype)

Bind this script to a keyboard shortcut to automatically type the username and
password and any other optional fields into the current window(terminal, browser, etc).
Auto-typed content is retrieved from the [pass](https://www.passwordstore.org/) password store.


If you have [issues with autotyped characters being dropped or changed](https://github.com/jordansissel/xdotool/issues/97), try running `setxkbmap` first. 


## Requirements

* Linux, Python 3 and the `python-libxdo` and `zenipy` modules are installed
* If you need to type more than the password, use the multiline format and store additional fields in each line.
* Maintain `.autotype` files for every `.gpg` file you want to be considered for autotype


## Features

* user maintained `.autotype` files to define window title matches and optionally the autotype sequence
* autotyping of arbitrary fields from the password entry and arbitrary autotype sequences, the default being `:user |Tab :password |Return`
* optional `BackSpace` press before entry of first field
* autotype speed setting
* support passwords in root password-store folder


## Usage

* Use your window manager or desktop environment to set up a keyboard shortcut
  that launches the `pass-autotyp3.py` script.
* Open a window where you want to autotype, and have the credentials in your
  `pass` store and an `autotype` file setup
* Place the cursor on the username field and press the keyboard shortcut defined above
* If there is more than one matching account for the window title, you'll be presented with a dialog to choose from.


### .gpg file syntax
```
mypassword
user: myusername
field1: another field

field2: one more field, with an optional empty line above
```

### .autotype file syntax

file with 3 different title match strings
```
git pull
git push
git clone
```

file with optional custom autotype sequnce including a custom field
```
:user |Tab :password |Tab :field1 |Return  
github - Mozilla Firefox
```

file with time delay autotype sequence 
```
:user !0.5 :password |Return
google
```
