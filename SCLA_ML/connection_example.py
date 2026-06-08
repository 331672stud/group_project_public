from SCLA_ML.app.SCLA_ML_vuln_scanner_client import VulnDetectorClient


client = VulnDetectorClient()


result = client.analyze('''"cursor.execute(SELECT * FROM ksksksksk WHERE id= (?)", abhjs)''')
print(result)


result = client.analyze('''"SELECT * FROM ksksksksk WHERE id= " + abhjs''')
print(result)


result = client.analyze('''"cursor.execute(SELECT * FROM ksksksksk WHERE id= (?)", abhjs)''')
print(result)


result = client.analyze('''"cursor.execute(SELECT * FROM ksksksksk WHERE id= (?)", abhjs)''')
print(result)


result = client.analyze('''"SELECT * FROM ksksksksk WHERE id= " + abhjs''')
print(result)



# answer should be:
# no vuln | SQL | no vuln | no vuln | SQL