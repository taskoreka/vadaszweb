from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from . forms import CreateUserForm, LoginForm,VadasztarsasagForm, PostForm, Beiraslekerdezes,BeirasFilterForm, AssignVadasztarsasagForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models  import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import BeiroForm, Krotaliafeltoltes, VadaszteruletForm, Krotáliahozzárendelés, FoglalasForm,  FoglaloForm, VadgazdalkodasijelentesForm, IdopontGeneratorForm
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from .models import Beiras, Vadfajtak, Vadfelek, Vadaszterulet, Idopont, Vadasztarsasag, UserProfil, Krotaliaszam
from datetime import datetime,  timedelta, time
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic import ListView, DetailView, CreateView,  DeleteView
from .models import Post, Comment, Follow
from .forms import CommentForm
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin,  UserPassesTestMixin
from .decorators import admin_required
from django.contrib.auth.models import User, Group
from django.db.models import Sum
from django.db.models import Q
from .decorators import group_required
from django.utils.decorators import method_decorator

@admin_required
def admin_dashboard(request):
    users = User.objects.all()
    posts = Post.objects.all()
    return render(request, 'main/admin_dashboard.html', {'users': users, 'posts': posts})

@group_required('vadasztarsasag')
def tarsasag_dash(request):
    return render(request,'main/tars_dashboard.html')

@group_required('vadasz')
def beiras_create_view(request):
    form = BeiroForm(user=request.user)
    if request.method == 'POST':
        form = BeiroForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = BeiroForm(user=request.user)
    return render(request, 'main/dashboard.html', {'form': form})


def load_vad(request):
    vadfajta_id = request.GET.get('vadfajta_id')
    if vadfajta_id:
        vadfelek = Vadfelek.objects.filter(vadfajta_id=vadfajta_id).order_by('neve')
        data = [{"id": vadfele.id, "neve": vadfele.neve} for vadfele in vadfelek]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

     
@group_required('vadasz')
def profilpage(request):
    beirasok = Beiras.objects.filter(user=request.user)  

    return render(request,'main/profil.html', {'beirasok':beirasok})
 

@group_required(['vadasztarsasag', 'rendszergazda'])
def teruletfoglalas(request):
    elerheto_idopontok = None

    if request.method == 'POST':
        form = FoglalasForm(request.POST)
        if form.is_valid():
            vadaszterulet = form.cleaned_data['vadaszterulet']
            datum = form.cleaned_data['datum']
            kezdesi_ido = form.cleaned_data['kezdesi_ido']
            befejezesi_ido = form.cleaned_data['befejezesi_ido']

           
            elerheto_idopontok = Idopont.objects.filter(
                vadaszterulet=vadaszterulet,
                datum=datum,
                foglalt=False
            ).exclude(
                kezdesi_ido__lt=befejezesi_ido,
                befejezesi_ido__gt=kezdesi_ido
            )
    else:
        form = FoglalasForm()

    return render(request, 'main/vadaszteruletek.html', {'form': form, 'elerheto_idopontok': elerheto_idopontok})


def homepage(request):
    return render(request,'main/home.html')

@group_required('hatosag')
def hatosag_dashboard(request):
    return render(request, 'main/hatosag_dashboard.html')

def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("mylogin")
        else:
            print("Form errors:", form.errors)

    context = {'registerform': form}
    return render(request, 'main/register.html', context=context)



def mylogin(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect("dashboard")
            
    context = {'loginform': form}
    
    return render(request,'main/mylogin.html', context=context)

class CustomLoginView(LoginView):
    template_name = 'main/mylogin.html'
    redirect_authenticated_user = True
    
    
    def get_success_url(self):
        
        user = self.request.user
        if user.groups.filter(name='vadasz').exists():
            return reverse_lazy('dashboard')  
        elif user.groups.filter(name='vadasztarsasag').exists():
            return reverse_lazy('tarsasag')  
        elif user.groups.filter(name='hatosag').exists():
            return reverse_lazy('hatosag') 
        elif user.groups.filter(name='rendszergazda').exists():
            return reverse_lazy('admin_dashboard')  
        else:
            return reverse_lazy('')

@group_required('vadasztarsasag')
def lekerdezesek(request):
    form = Beiraslekerdezes(request.GET or None)
    query = Beiras.objects.all()

    if form.is_valid():
        vadasz_nev= form.cleaned_data.get('vadasz_nev')
        kezdo_ido = form.cleaned_data.get('kezdo_ido')
        vege_ido = form.cleaned_data.get('vege_ido')
        vadfajta = form.cleaned_data.get('vadfajta')
        vadfele = form.cleaned_data.get('vadfele')

        if vadasz_nev:
            query = query.filter(name__icontains=vadasz_nev)
        if kezdo_ido and vege_ido:
            query = query.filter(date__range=(kezdo_ido, vege_ido))
        if vadfajta:
            query = query.filter(vadfajta=vadfajta)
        if vadfele:
            query = query.filter(vadfele=vadfele)


    return render(request, 'main/lekerdezes.html', {'form': form, 'results': query})

@group_required('hatosag')
def krotalia_feltolt(request):
    if request.method == 'POST':
        form =Krotaliafeltoltes(request.POST)
        if form.is_valid():
            krotalia = form.save(commit=False)
            krotalia.tulajdonos = request.user
            krotalia.save()
            return redirect('hatosag')  
    else:
        form = Krotaliafeltoltes()

    return render(request, 'main/krotaliafel.html', {'form': form})

@group_required(['vadasztarsasag', 'hatosag'])
def krotalia_atadas(request):
    if request.method == 'POST':
        form = Krotáliahozzárendelés(request.POST, user=request.user)
        if form.is_valid():
            krotalia = form.cleaned_data['krotalia']
            uj_tulajdonos = form.cleaned_data['uj_tulajdonos']
            krotalia.tulajdonos = uj_tulajdonos
            krotalia.atado = request.user
            krotalia.save()
            messages.success(request, 'Átadás sikeresen megtörtént.')
            return redirect('krotaliaatadas')
    else:
        form = Krotáliahozzárendelés(user=request.user)

    return render(request, 'main/krotaliaatadas.html', {'form': form})

@group_required('vadasz')
def dashboard(request):
    if request.user.is_authenticated:
        foglalasok = Idopont.objects.filter(user=request.user)  
    else:
        foglalasok = []

    return render(request, 'main/dashboard.html', {'foglalasok': foglalasok})

@group_required(['vadasztarsasag', 'vadasz'])
def foglalas_create_view(request):
    if request.method == 'POST':
        form = FoglaloForm(request.POST, user=request.user)
        if form.is_valid():
            vadaszterulet = form.cleaned_data['vadaszterulet']
            datum = form.cleaned_data['datum']
            kezdesi_ido = form.cleaned_data['kezdesi_ido']
            befejezesi_ido = form.cleaned_data['befejezesi_ido']

            
            foglalt = Idopont.objects.filter(
                vadaszterulet=vadaszterulet,
                datum=datum,
                kezdesi_ido__lt=befejezesi_ido,
                befejezesi_ido__gt=kezdesi_ido
            ).exists()

            if foglalt:
                messages.error(request, 'Ez az időpont már foglalt ezen a területen.')
            else:
                
                foglalas = form.save(commit=False)
                foglalas.user = request.user
                foglalas.save()
                messages.success(request, 'Foglalás sikeresen megtörtént.')
                return redirect('foglalas') 
    else:
        form = FoglaloForm(user=request.user)

    return render(request, 'main/foglalas.html', {'form': form})


@group_required('vadasz')
def foglalasaim(request):
    current_datetime = timezone.localtime(timezone.now())
    today = current_datetime.date()
    now = current_datetime.time()
    
    aktiv_foglalasok = Idopont.objects.filter(
        user=request.user,
        datum__gte=today,
    ).exclude(
    datum=today, befejezesi_ido__lte=now
    )


    nem_kezdodott_el = aktiv_foglalasok.filter(datum__gt=today) | aktiv_foglalasok.filter(datum=today, kezdesi_ido__gt=now)
    elkezdodott_nincsvege = aktiv_foglalasok.filter(datum=today, kezdesi_ido__lte=now, befejezesi_ido__gt=now)

    return render(request, 'main/foglalasaim.html', {
        'nem_kezdodott_el': nem_kezdodott_el,
        'elkezdodott_nincsvege': elkezdodott_nincsvege,
    })

@group_required('vadasz')
def foglalas_torlese(request, idopont_id):
    idopont = get_object_or_404(Idopont, id=idopont_id, user=request.user)
    idopont.delete()
    return redirect('foglalasaim')

@group_required('vadasz')
def vadaszat_befejezese(request, idopont_id):
   idopont = get_object_or_404(Idopont, id=idopont_id, user=request.user)
   initial_data = {
        'user' : idopont.user,
        'teljes_nev': idopont.teljes_nev,
        'datum': idopont.datum,
        'kezdeti_ido': idopont.kezdesi_ido,
        'vege_ido': idopont.befejezesi_ido,
        'vadaszat_helye': idopont.vadaszterulet,
    }
   if request.method == 'POST':
    form = BeiroForm(request.POST, initial=initial_data, user=request.user)  
    if form.is_valid():
            krotalia = form.save(commit=False)
            form.save()
            return redirect('dashboard')
    else:
            return render(request, 'main/beiro.html', {'form': form, 'error': 'A beírás érvénytelen!'})
    
   else: 
        form = BeiroForm(initial=initial_data, user=request.user)
        return render(request, 'main/beiro.html', {'form':form})
    
@group_required('vadasz')
def sajat_krotaliak(request):
    felhasznalt_krotaliak = Beiras.objects.filter(krotalia__isnull=False).values_list('krotalia_id', flat=True)
    krotaliak = Krotaliaszam.objects.filter(tulajdonos=request.user).exclude(id__in=felhasznalt_krotaliak)
    return render(request, 'main/sajat_krotaliak.html', {'krotaliak': krotaliak})

@method_decorator(group_required(['vadasztarsasag', 'vadasz']), name='dispatch')
class PostListView(ListView):
    model = Post
    template_name = "main/post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        if self.request.user.groups.filter(name='vadasztarsasag').exists():
            vadasztarsasag = Vadasztarsasag.objects.get(vadasztarsasag=self.request.user)
            return Post.objects.filter(vadasztarsasag=vadasztarsasag)
        elif hasattr(self.request.user, 'userprofil') and self.request.user.userprofil.vadasztarsasag:
            return Post.objects.filter(vadasztarsasag=self.request.user.userprofil.vadasztarsasag)
        return Post.objects.none()

@method_decorator(group_required(['vadasztarsasag', 'vadasz']), name='dispatch')
class PostDetailView(DetailView):
    model = Post
    template_name = "main/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        post = self.get_object()
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=post.pk)
        return self.get(request, *args, **kwargs)

@method_decorator(group_required(['vadasztarsasag', 'vadasz']), name='dispatch')
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'main/posztolas.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        if self.request.user.groups.filter(name='vadasztarsasag').exists():
            form.instance.vadasztarsasag = Vadasztarsasag.objects.get(vadasztarsasag=self.request.user)
        elif hasattr(self.request.user, 'userprofil') and self.request.user.userprofil.vadasztarsasag:
            form.instance.vadasztarsasag = self.request.user.userprofil.vadasztarsasag
        else:
            form.add_error(None, "Nem tartozol vadásztársasághoz, vagy nem vagy vadásztársasági admin.")
            return self.form_invalid(form)
        return super().form_valid(form)
    
@admin_required
def idopont_generator(request):
    if request.method == 'POST':
        form = IdopontGeneratorForm(request.POST)
        if form.is_valid():
            kezdo_datum = form.cleaned_data['kezdo_datum']
            veg_datum = form.cleaned_data['veg_datum']
            vadaszterulet = form.cleaned_data['vadaszterulet']
            mindet_kivalaszt = form.cleaned_data['mindet_kivalaszt']
            
            if mindet_kivalaszt:
                vadaszteruletek = Vadaszterulet.objects.all()
            else:
                vadaszteruletek = form.cleaned_data['vadaszteruletek']
            
            if not vadaszteruletek:
                messages.error(request, 'Legalább egy vadászterületet ki kell választani!')
                return render(request, 'main/idopont_generator.html', {'form': form})
                

            for vadaszterulet in vadaszteruletek:
                jelenlegi_datum = kezdo_datum
                while jelenlegi_datum <= veg_datum:
                    kezdesi_ido = time(5, 0) 
                    befejezesi_ido = time(22, 0)
                    lepes = timedelta(minutes=30)
                
                while kezdesi_ido < befejezesi_ido:
                    veg_ido = (datetime.combine(jelenlegi_datum, kezdesi_ido) + lepes).time()
                    Idopont.objects.create(
                        vadaszterulet=vadaszterulet,
                        datum=jelenlegi_datum,
                        kezdesi_ido=kezdesi_ido,
                        befejezesi_ido=veg_ido,
                        foglalt=False
                    )
                    kezdesi_ido = veg_ido
                
                jelenlegi_datum += timedelta(days=1)
            
            messages.success(request, 'Időpontok sikeresen generálva!')
        else:
            messages.error(request, 'Hibás adatok!')

    else:
        form = IdopontGeneratorForm()

    return render(request, 'main/idopont_generator.html', {'form': form})

@admin_required
def jog_kezeles(request):
    users = User.objects.all()
    groups = Group.objects.all()

    if request.method == "POST":
        user_id = request.POST.get('user_id')
        group_id = request.POST.get('group_id')
        action = request.POST.get('action')

        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)

            if action == "add":
                user.groups.add(group)
                messages.success(request, f"{user.username} hozzáadva a(z) {group.name} csoporthoz.")
            elif action == "remove":
                user.groups.remove(group)
                messages.success(request, f"{user.username} eltávolítva a(z) {group.name} csoportból.")
        except User.DoesNotExist:
            messages.error(request, "A felhasználó nem található.")
        except Group.DoesNotExist:
            messages.error(request, "A csoport nem található.")

    return render(request, 'main/jogosultsagkezeles.html', {
        'users': users,
        'groups': groups,
    })

@admin_required
def vadasztarsasag_list(request):
    vadasztarsasagok = Vadasztarsasag.objects.all()
    return render(request, 'main/vadasztarsasag_list.html', {'vadasztarsasagok': vadasztarsasagok})

@admin_required
def assign_vadaszok(request, vadasztarsasag_id):
    vadasztarsasag = get_object_or_404(Vadasztarsasag, id=vadasztarsasag_id)
    all_users = User.objects.filter(groups__name='vadasz')  
    
    if request.method == 'POST':
        selected_vadasz_ids = request.POST.getlist('vadaszok')  
        selected_vadaszok = User.objects.filter(id__in=selected_vadasz_ids)
        vadasztarsasag.vadaszok.set(selected_vadaszok)  
        return redirect('vadasztarsasag_list')  
    
    context = {
        'vadasztarsasag': vadasztarsasag,
        'all_users': all_users,
    }
    return render(request, 'main/assign_vadaszok.html', context)

@admin_required
def assign_vadasztarsasag_view(request):
    if request.method == 'POST':
        form = AssignVadasztarsasagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'A vadásztársaság sikeresen hozzárendelve egy vadászati hatósághoz!')
            return redirect('assign_vadasztarsasag')
    else:
        form = AssignVadasztarsasagForm()

    return render(request, 'main/assign_vadasztarsasag.html', {'form': form})

@method_decorator(group_required('vadasztarsasag'), name='dispatch')
class VadaszteruletListView(LoginRequiredMixin, ListView):
    model = Vadaszterulet
    template_name = 'main/vadaszteruletek_list.html' 
    context_object_name = 'vadaszteruletek'

    def get_queryset(self):
        return Vadaszterulet.objects.filter(vadasztarsasag__vadasztarsasag=self.request.user)

@method_decorator(group_required('vadasztarsasag'), name='dispatch')
class VadaszteruletCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Vadaszterulet
    form_class = VadaszteruletForm
    template_name = 'main/vadaszterulet_form.html'

    def form_valid(self, form):
        form.instance.vadasztarsasag = Vadasztarsasag.objects.get(vadasztarsasag=self.request.user)
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.groups.filter(name='vadasztarsasag').exists()

@method_decorator(group_required('vadasztarsasag'), name='dispatch')
class VadaszteruletDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Vadaszterulet
    template_name = 'main/vadaszterulet_confirm_delete.html' 
    success_url = reverse_lazy('vadaszteruletek_list')

    def test_func(self):
        vadaszterulet = self.get_object()
        return vadaszterulet.vadasztarsasag.vadasztarsasag == self.request.user

@group_required('vadasztarsasag')
def beiras_list_view(request):
    if not request.user.groups.filter(name='vadasztarsasag').exists():
        return render(request, 'main/permission_denied.html')
    try:
        vadasztarsasag = Vadasztarsasag.objects.get(vadasztarsasag=request.user)
    except Vadasztarsasag.DoesNotExist:
        return render(request, 'main/no_data.html', {'message': 'Nem tartozik vadásztársasághoz.'})

    vadaszteruletek = vadasztarsasag.vadaszteruletek.all()
    beirasok = Beiras.objects.filter(vadaszat_helye__in=[terulet.vadaszterulet for terulet in vadaszteruletek])

    total_darabszam = None
    if request.method == 'GET':
        filter_form = BeirasFilterForm(request.GET)
        if filter_form.is_valid():
            krotaliaszam = filter_form.cleaned_data.get('krotaliaszam')
            vadasz_neve = filter_form.cleaned_data.get('vadasz_neve')
            datum_kezdete = filter_form.cleaned_data.get('datum_kezdete')
            datum_vege = filter_form.cleaned_data.get('datum_vege')
            vadfajta = filter_form.cleaned_data.get('vadfajta')
            vadfele = filter_form.cleaned_data.get('vadfele')

            if krotaliaszam:
                beirasok = beirasok.filter(krotalia__icontains=krotaliaszam)
            if vadasz_neve:
                beirasok = beirasok.filter(vadasz_neve__icontains=vadasz_neve)
            if datum_kezdete:
                beirasok = beirasok.filter(datum__gte=datum_kezdete)
            if datum_vege:
                beirasok = beirasok.filter(datum__lte=datum_vege)
            if vadfajta:
                beirasok = beirasok.filter(vadfajta=vadfajta)
            if vadfele:
                beirasok = beirasok.filter(vadfele=vadfele)

            total_darabszam = beirasok.aggregate(Sum('darabszam'))['darabszam__sum'] or 0
    else:
        filter_form = BeirasFilterForm(user=request.user)

    context = {
        'beirasok': beirasok,
        'filter_form': filter_form,
        'total_darabszam': total_darabszam,
    }
    return render(request, 'main/beiras_list.html', context)

def user_logout(request):
    logout(request)
    return redirect('') 

