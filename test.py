import yaml

dict_file = {'server': {'URLDTBS': 'jdbc:postgresql://192.168.99.102:5432/wizards1', "USR": "postgres",
                         "PASSWORD": "postgres",
                         "SECRET": "wizardSecretKey",
                         "EXPIRED": 86400000,
                         "PORT": 8081},
             'proxy': {'PORT': 8081},
             'client': {'PORT': 3000}}

with open(r'settings.yaml', 'w') as file:
    documents = yaml.dump(dict_file, file)


with open(r'settings.yaml') as file:
    doc = yaml.load(file, Loader=yaml.FullLoader)
    print(doc['server'])
