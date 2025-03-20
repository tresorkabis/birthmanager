from django.db import models

# Create your models here.

class Pays(models.Model):
    nom = models.CharField(max_length=50)
    
class Ville(models.Model):
    nom = models.CharField(max_length=50)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE)

class Parent(models.Model):
    id_parent =models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50)
    postnom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    sexe = models.CharField(max_length=1)
    date_naisssance = models.DateField()
    lieu_naissance = models.CharField(max_length=50)
    role = models.CharField(max_length=30)
    profession = models.CharField(max_length=30)
    adresse = models.CharField(max_length=200)
    telephone = models.CharField(max_length=15)

class Hopital(models.Model):
    nom = models.CharField(max_length=50)
    adresse = models.CharField(max_length=200)
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE)

class Medecin(models.Model):
    nom = models.CharField(max_length=50)
    postnom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    sexe = models.CharField(max_length=1)
    cnom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=200)
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE)

class Personne(models.Model):
    nom = models.CharField(max_length=50)
    postnom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    sexe = models.CharField(max_length=1)
    date_naisssance = models.DateField()
    lieu_naissance = models.ForeignKey(Ville, on_delete=models.CASCADE)
    pere = models.Foreignkey(Parent,on_delete=models.CASCADE)
    mere = models.Foreignkey(Parent,on_delete=models.CASCADE)
    medecin = models.Foreignkey(Medecin,on_delete=models.CASCADE)
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='personnes_vivant')
    enregistre_par = models.CharFielld(max_length=100, related_name='bourgmestre')
    


    
