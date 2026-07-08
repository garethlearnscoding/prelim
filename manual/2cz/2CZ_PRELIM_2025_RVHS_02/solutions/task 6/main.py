from flask import Flask, render_template, url_for
import os, sqlite3

app = Flask(__name__)

def voting_result(conn):
    sql = '''
        SELECT groups.name, groups.group_id, COUNT(*) FROM votes
            JOIN groups ON groups.group_id = votes.vote  
        GROUP BY votes.vote
        ORDER BY COUNT(*) DESC
    '''
    cur = conn.execute(sql)
    result = cur.fetchall()
    for row in result:
        print(f'{row[0]:20} ({row[1]}) - {row[2]}')
    return (result[0][1], result)

def get_details(conn, group_id):
    sql = '''
        SELECT groups.name, candidates.name FROM groups
            JOIN candidate_group ON groups.group_id = candidate_group.group_id
            JOIN candidates ON candidates.candidate_id = candidate_group.candidate_id
        WHERE groups.group_id = ?
    '''
    cur = conn.execute(sql, (group_id,))
    details = cur.fetchall()
    #print(details)
    print_out = f'{details[0][0]} - \n'
    for detail in details:
        print_out += detail[1] + '\n'
    print(print_out[:-1])
    return details

conn = sqlite3.connect('sc_election_2025.db')

@app.route("/")
def index():
    conn = sqlite3.connect("sc_election_2025.db")
    group_id, result = voting_result(conn)
    details = get_details(conn, group_id)
    conn.close()
    return render_template("index.html", result=result, details=details)

if __name__ == "__main__":
    app.run ("127.0.0.1", port=15000)
