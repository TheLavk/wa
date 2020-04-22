import sqlite3
import os
import datetime
from flask import Flask, render_template, redirect, session
from flask_wtf import FlaskForm
from wtforms import TextAreaField,validators
from wtforms import RadioField
from wtforms.validators import DataRequired,Length

app = Flask(__name__)
app.debug = True
app.secret_key = 'jsafiklj llajsflkjalwfjikaw1'

aktualni_adresar = os.path.abspath(os.path.dirname(__file__))
databaze = (os.path.join(aktualni_adresar, 'pozn.db'))

class PoznamkaForm(FlaskForm):
    poznamka = TextAreaField("Poznamka", validators=[DataRequired()])
    dulezitost = RadioField("Dulezitost", choices=[("1", 'poznámka'), ("2", 'důležitější poznámka'), ("3", 'velice důležitá poznámka')])

@app.route('/poznamky/vlozit', methods=['GET', 'POST'])
def zapsat_poznamku():
    textdelka=250
    form = PoznamkaForm()
    poznamky_text = form.poznamka.data
    dulezitost = form.dulezitost.data
    if form.validate_on_submit():
        if len(poznamky_text) > textdelka:
         return render_template('index.html', form=form, error="Překročil jsi limit 250 znaků." + str(len(poznamky_text)))
        else:
         conn = sqlite3.connect(databaze)
         c = conn.cursor()
         x = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
         c.execute(f"INSERT INTO poznamky(pozn,datum,dulezitost) VALUES ('{poznamky_text}','{x}','{dulezitost}')")
         conn.commit()
         conn.close()
         return redirect('/')
    return render_template('index.html', form=form)


@app.route('/')
def zobraz_poznamky():
    conn = sqlite3.connect(databaze)
    c = conn.cursor()
    poznamky = c.fetchall()
    """tady jsem zmenil select *"""
    c.execute('SELECT rowid, pozn, datum, dulezitost FROM poznamky ORDER BY datum desc')
    poznamky2=c.fetchall()
    poznamky=c.fetchall()
    datum=[]
    for row in poznamky2:
        poznamky.append(row[0])
        datum.append(row[1])
    conn.close()
    return render_template('pozn.html', poznamky=poznamky2, datum=datum)

@app.route('/smaz/<int:poznamky_id>')
def smaz_poznamku(poznamky_id):
    """Smaže vybranou poznámku"""
    conn = sqlite3.connect(databaze)
    c = conn.cursor()
    # Aby nedošlo k útoku SQL injection na vaší aplikaci! Viz. nahoře.
    c.execute("DELETE FROM poznamky WHERE rowid=?", (poznamky_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/uprav/<int:poznamky_id>', methods=['GET', 'POST'])
def uprav_poznamku(poznamky_id):
    """Upraví poznámku."""
    # Potřebujeme získat poznámku z databáze
    conn = sqlite3.connect(databaze)
    c = conn.cursor()
    # Poznámku získáme výběrem z databáze, kdy hledáme řádek s id poznámky
    c.execute("SELECT pozn, datum, dulezitost FROM poznamky WHERE rowid=?", (poznamky_id,))
    # Dotazem získám seznam (n-tici) s daty
    poznamka_tuple = c.fetchone()
    conn.close()
    # Naplnění formuláře daty z databáze
    form = PoznamkaForm(poznamka=poznamka_tuple[0])
    poznamky_text = form.poznamka.data
    dulezitost = form.dulezitost.data
    if form.validate_on_submit():
        conn = sqlite3.connect(databaze)
        c = conn.cursor()
        # Podívejte se sem!!!:
        # https://docs.python.org/3/library/sqlite3.html
        # a hledejte text: Never do this -- insecure!
        # Aby nedošlo k útoku SQL injection na vaší aplikaci:
        c.execute("UPDATE poznamky SET pozn=?, dulezitost=? WHERE rowid=?", (poznamky_text, dulezitost, poznamky_id,))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('index.html', form=form)




if __name__ == '__main__':
    app.run()
