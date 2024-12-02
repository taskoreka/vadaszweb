from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import PasswordInput, TextInput
from .models import Beiras, Vadfelek, Vadfajtak,Post, Krotaliaszam, UserProfil, Vadaszterulet,Vadasztarsasag, Idopont, Vadgazdalkodasijelentes
from django import forms
from .models import Comment

class CreateUserForm(UserCreationForm):
    teljes_nev = forms.CharField(max_length=100, required=True)
    vadaszjegyid = forms.CharField(max_length=12, required=True)
    class Meta:
        model = User
        fields=['username', 'teljes_nev', 'email', 'vadaszjegyid','password1', 'password2']
        labels = {
        "username":  "Felhasználónév",
        "teljes_nev": "Teljes név:",
        "email": "E-mail cím:",
        "vadaszjegyid": "Vadászjegy azonosítója",
        "password1": "Jelszó",
        "password2": "Jelszó mégegyszer",
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            UserProfil.objects.create(
                user=user,
                teljes_nev=self.cleaned_data.get('teljes_nev', ''),
                vadaszjegyid=self.cleaned_data.get('vadaszjegyid', '')
            )
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(), label="Felhasználónév")
    password =forms.CharField(widget=PasswordInput(), label="Jelszó")



class BeiroForm(forms.ModelForm):
    class Meta:
        model = Beiras
        fields = ['user', 'vadasz_neve', 'datum', 'kezdeti_ido', 'vege_ido', 'vadaszat_helye', 'vadfajta', 'vadfele', 'darabszam', 'krotalia','megjegyzes', 'kep']
        labels ={
            "user" : "Felhsználónév:",
            "vadasz_neve":"Vadász neve",
            "datum":"Dátum",
            "kezdeti_ido": "Kezdés ideje",
            "vege_ido" : "Befejezés ideje",
            "vadaszat_helye": "Vadászterület",
            "vadfajta":"Vadfajta",
            "vadfele":"Vadféle",
            "darabszam": "Darabszám", 
            "krotalia":"Krotáliaszám:",
            "megjegyzes": "Megjegyzés",
            "kep": "Kép"
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)
        
        
        if user:
            felhasznalt_krotaliak = Beiras.objects.filter(krotalia__isnull=False).values_list('krotalia_id', flat=True)
            self.fields['krotalia'].queryset = Krotaliaszam.objects.filter(tulajdonos=user).exclude(id__in=felhasznalt_krotaliak)


        
        self.fields['vadfele'].queryset = Vadfelek.objects.none()

        
        if 'vadfajta' in self.data:
            try:
                vadfajta_id = int(self.data.get('vadfajta'))
                self.fields['vadfele'].queryset = Vadfelek.objects.filter(vadfajta_id=vadfajta_id).order_by('neve')
            except (ValueError, TypeError):
                pass  
        
        elif self.instance.pk:
            self.fields['vadfele'].queryset = Vadfelek.objects.filter(vadfajta=self.instance.vadfele.vadfajta).order_by('neve')
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        
        if instance.krotalia:
            try:
                
                krotalia = Krotaliaszam.objects.get(nagyvadazonosito=instance.krotalia)
                krotalia.delete()
            except Krotaliaszam.DoesNotExist:
                pass  

        if commit:
            instance.save()
        return instance


class Beiraslekerdezes(forms.Form):
    vadasz_nev = forms.CharField(required=False, label='Vadász neve')
    kezdo_ido = forms.DateField(required=False, label='Kezdő dátum', widget=forms.DateInput(attrs={'type': 'date'}))
    vege_ido = forms.DateField(required=False, label='Vége dátum', widget=forms.DateInput(attrs={'type': 'date'}))
    vadfajta = forms.ChoiceField(
        required=False,
        label='Vadfajta',
        choices=[('', '---------')] + [(vadfajta.id, vadfajta.neve) for vadfajta in Vadfajtak.objects.all()]
    )
    vadfele = forms.ChoiceField(
        required=False,
        label='Vadféle',
        choices=[('', '---------')] + [(vadfele.id, vadfele.neve) for vadfele in Vadfelek.objects.all()]
    )

class Krotaliafeltoltes(forms.ModelForm):
    class Meta:
        model = Krotaliaszam
        fields = ['nagyvadazonosito']
        labels ={
            "nagyvadazonosito": "Nagyvadazonosító szám",
        }

class Krotáliahozzárendelés(forms.Form):
    krotalia = forms.ModelChoiceField(queryset=Krotaliaszam.objects.none(), label='Nagyvadazonosító kiválasztása')
    uj_tulajdonos = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Új tulajdonos (vadász)",
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        
        if user:
            self.fields['krotalia'].queryset = Krotaliaszam.objects.filter(tulajdonos=user)

            
            if user.groups.filter(name='hatosag').exists():
                self.fields['uj_tulajdonos'].queryset = User.objects.filter(
                    vadasztarsasag__in=user.assigned_vadasztarsasagok.all()
                )
            
            elif user.groups.filter(name='vadasztarsasag').exists():
                try:
                    vadasztarsasag = user.vadasztarsasag  
                    self.fields['uj_tulajdonos'].queryset = vadasztarsasag.vadaszok.all()
                except AttributeError:
                    self.fields['uj_tulajdonos'].queryset = User.objects.none()

                
                self.fields['uj_tulajdonos'].label_from_instance = lambda obj: obj.userprofil.teljes_nev if hasattr(obj, 'userprofil') else obj.username

class FoglalasForm(forms.Form):
    vadaszterulet = forms.ModelChoiceField(queryset=Vadaszterulet.objects.all(), label='Vadaszterulet kiválasztása')
    datum = forms.DateField(widget=forms.SelectDateWidget, label='Dátum kiválasztása')
    kezdesi_ido = forms.TimeField(widget=forms.TimeInput(format='%H:%M'), label='Kezdési idő')
    befejezesi_ido = forms.TimeField(widget=forms.TimeInput(format='%H:%M'), label='Befejezési idő')

class FoglaloForm(forms.ModelForm):
    class Meta:
        model = Idopont
        fields = ['teljes_nev', 'vadaszterulet', 'datum', 'kezdesi_ido', 'befejezesi_ido']
        widgets = {
            'datum': forms.DateInput(attrs={'type': 'date'}),
            'kezdesi_ido': forms.TimeInput(attrs={'type': 'time'}),
            'befejezesi_ido': forms.TimeInput(attrs={'type': 'time'}),
        }
        labels = {
        "teljes_nev":  "Név:",
        "vadaszterulet": "Vadászterület:",
        "datum": "Dátum:",
        "kezdesi_ido": "Kezdési idő:",
        "befejezesi_ido": "Befejezési idő:",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)  
        if user:
            try:
                user_profil = user.userprofil  
                self.fields['teljes_nev'].initial = user_profil.teljes_nev
            except UserProfil.DoesNotExist:
                pass  

        
        if 'vadaszterulet' in self.fields:
            self.fields['vadaszterulet'].queryset = Vadaszterulet.objects.all()

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Add meg a poszt címét'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Írd ide a poszt tartalmát'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Írj egy hozzászólást...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class IdopontGeneratorForm(forms.Form):
    kezdo_datum = forms.DateField(label='Kezdődátum', widget=forms.SelectDateWidget(attrs={
            'class': 'form-select' 
        }))
    veg_datum = forms.DateField(label='Záródátum', widget=forms.SelectDateWidget(attrs={
            'class': 'form-select' 
        }))
    vadaszteruletek = forms.ModelMultipleChoiceField(
        queryset=Vadaszterulet.objects.select_related('vadasztarsasag'),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'  
        }),
        required=False,
        label="Vadászterületek",
        to_field_name='id')

    mindet_kivalaszt = forms.BooleanField(
        required=False,
        label="Mindet kiválaszt",
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'  
        })
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vadaszteruletek'].label_from_instance = lambda obj: f"{obj.vadaszterulet} ({obj.vadasztarsasag.vadasztarsasag})"

class VadasztarsasagForm(forms.ModelForm):
    vadaszok = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(groups__name='vadasz'),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Vadasztarsasag
        fields = ['vadasztarsasag', 'vad_hatosag', 'vadaszok']

class AssignVadasztarsasagForm(forms.ModelForm):
    class Meta:
        model = Vadasztarsasag
        fields = ['vadasztarsasag', 'vad_hatosag']
        widgets = {
            'vadasztarsasag': forms.Select(attrs={'class': 'form-control'}),
            'vad_hatosag': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'vadasztarsasag':"Vadásztársaság",
            'vad_hatosag': "Vadászati hatóság",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['vadasztarsasag'].queryset = User.objects.filter(groups__name='vadasztarsasag')
        self.fields['vad_hatosag'].queryset = User.objects.filter(groups__name='hatosag')

class VadaszteruletForm(forms.ModelForm):
    class Meta:
        model = Vadaszterulet
        fields = ['vadaszterulet']
        widgets = {
            'vadaszterulet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vadászterület neve'}),
        }

class BeirasFilterForm(forms.Form):
    vadasz_neve = forms.CharField(required=False, label='Vadász neve')
    datum_kezdete = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Dátum - Kezdete'
    )
    datum_vege = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Dátum - Vége'
    )
    vadfajta = forms.ModelChoiceField(
        queryset=Vadfajtak.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Vadfajta'
    )
    vadfele = forms.ModelChoiceField(
        queryset=Vadfelek.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Vadféle'
    )
    krotaliaszam = forms.CharField(
        max_length=50, 
        required=False, 
        label="Krotáliaszám", 
        widget=forms.TextInput)
    
class VadgazdalkodasijelentesForm(forms.ModelForm):
    class Meta:
        model = Vadgazdalkodasijelentes
        fields = ['file']
     

