from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from datetime import date
from django.core.mail import send_mail
from django.utils.timezone import now
from django.contrib.messages import add_message, INFO
from datetime import timedelta

   

class Vadasztarsasag(models.Model):
    vadasztarsasag = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'vadasztarsasag'})
    vad_hatosag = models.ForeignKey(User, related_name='assigned_vadasztarsasagok', on_delete=models.CASCADE)
    vadaszok = models.ManyToManyField(User, related_name='vadaszok', blank=True)

    def __str__(self):
        return self.vadasztarsasag.username

class UserProfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    teljes_nev = models.CharField(max_length=100, blank=True)
    vadaszjegyid = models.CharField(max_length=12, blank=True)
    vadasztarsasag = models.ManyToManyField(Vadasztarsasag, blank=True)

    def __str__(self):
        return self.teljes_nev or self.user.username

class Vadfajtak(models.Model):
    neve = models.CharField(max_length=40)

    def __str__(self):
        return self.neve


class Vadfelek(models.Model):
    vadfajta = models.ForeignKey(Vadfajtak, on_delete=models.CASCADE)
    neve = models.CharField(max_length=40)

    def __str__(self):
        return self.neve

class Krotaliaszam(models.Model):
    nagyvadazonosito = models.CharField(max_length=16)
    tulajdonos = models.ForeignKey(User, on_delete=models.CASCADE, related_name='krotalia')
    atado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='atadott_krotaliak')

    def __str__(self):
        return f'Krotáliaszám: {self.nagyvadazonosito} (Tulajdonos: {self.tulajdonos.username})'

class Beiras(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    vadasz_neve = models.CharField(max_length=50)
    datum = models.DateField(default=date.today)
    kezdeti_ido = models.TimeField()
    vadaszat_helye = models.CharField(max_length=50)
    vege_ido = models.TimeField()
    vadfajta = models.ForeignKey(Vadfajtak, on_delete=models.SET_NULL, blank=True, null=True)
    vadfele = models.ForeignKey(Vadfelek, on_delete=models.SET_NULL, blank=True, null=True)
    darabszam = models.IntegerField(blank=True, null=True)
    krotalia = models.ForeignKey(Krotaliaszam, on_delete=models.SET_NULL, blank=True, null=True, unique=True) 
    megjegyzes = models.CharField(max_length=50, blank=True, null=True)
    kep = models.ImageField(upload_to='beiras_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.vadasz_neve} - {self.datum}"
    def save(self, *args, **kwargs):
        
        super().save(*args, **kwargs)  

        
        trofeabiralati_vadak = {
            'vaddisznó': ['kan'],
            'muflon': ['kos'],
            'gímszarvas': ['bika'],
            'dámszarvas': ['bika'],
            'őz': ['bak']
        }

        if (
            self.vadfajta and self.vadfele and
            self.vadfajta.neve in trofeabiralati_vadak and
            self.vadfele.neve in trofeabiralati_vadak[self.vadfajta.neve]
        ):
            
            ertekeles_hatarido = self.datum + timedelta(days=30)
            uzenet = (
                f"Trófeabírálatra {ertekeles_hatarido.strftime('%Y-%m-%d')}-ig kell(het) "
                f"vinned az elejtett {self.vadfajta.neve} {self.vadfele.neve} trófeáját!"
            )

            
            if self.user and self.user.email:
                send_mail(
                    subject="Trófeabírálati Értesítés",
                    message=uzenet,
                    from_email="admin@vadasztarsasag.hu",
                    recipient_list=[self.user.email]
                )

            
            if hasattr(self, 'request'):
                add_message(self.request, INFO, uzenet)

class Vadaszterulet(models.Model):
    vadasztarsasag = models.ForeignKey(Vadasztarsasag, on_delete=models.CASCADE, related_name='vadaszteruletek')
    vadaszterulet = models.CharField(max_length=100)
    def __str__(self):
        return self.vadaszterulet
    
class Idopont(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    teljes_nev = models.CharField(max_length=100)
    vadaszterulet = models.ForeignKey(Vadaszterulet, on_delete=models.CASCADE)
    datum = models.DateField()
    kezdesi_ido = models.TimeField()
    befejezesi_ido = models.TimeField()
    foglalt = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.teljes_nev} - {self.vadaszterulet} - {self.datum}"


    
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    vadasztarsasag = models.ForeignKey(Vadasztarsasag, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='comment_images/', blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='followers')
    followed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} follows {self.post}"
    
class Vadgazdalkodasijelentes(models.Model):
    file = models.FileField(upload_to='uploads/')
    feltoltve = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
    
