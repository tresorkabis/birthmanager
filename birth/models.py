from django.db import models

from birth.utils import SEXES
from users.models import User

# Create your models here.

class Pays(models.Model):
    nom = models.CharField(max_length=50)

    def __str__(self):
        return self.nom
    
class Ville(models.Model):
    nom = models.CharField(max_length=50)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom

class Parent(models.Model):
    nom = models.CharField(max_length=50)
    postnom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    sexe = models.CharField(max_length=1, choices=SEXES)
    date_naisssance = models.DateField()
    lieu_naissance = models.CharField(max_length=50)
    role = models.CharField(max_length=30)
    profession = models.CharField(max_length=30)
    adresse = models.TextField()
    telephone = models.CharField(max_length=15)

    def __str__(self):
        return self.nom

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
    pere = models.ForeignKey(Parent,on_delete=models.CASCADE, related_name='pere')
    mere = models.ForeignKey(Parent,on_delete=models.CASCADE, related_name='mere')
    medecin = models.ForeignKey(Medecin,on_delete=models.CASCADE)
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE, null=True, blank=True)
    enregistre_par = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='enregistre_par')
    photo_url = models.ImageField(upload_to='photos/', blank=True, null=True)
    


    
