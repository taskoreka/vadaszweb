from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from main.models import Idopont, Vadaszterulet

class Command(BaseCommand):
    help = 'Szabad időpontok generálása'

    def handle(self, *args, **kwargs):
        
        vadaszterulet = Vadaszterulet.objects.get(id=4)
        
        
        datum = datetime(2024, 11, 17).date()
        
        
        kezdesi_ido = datetime(2024, 11, 17, 5, 0)
        befejezesi_ido = datetime(2024, 11, 17, 22, 0)
        lepes = timedelta(minutes=30)

        while kezdesi_ido < befejezesi_ido:
            veg_ido = kezdesi_ido + lepes
            
            Idopont.objects.create(
                vadaszterulet=vadaszterulet,
                datum=datum,
                kezdesi_ido=kezdesi_ido.time(),
                befejezesi_ido=veg_ido.time(),
                foglalt=False
            )
            kezdesi_ido = veg_ido

        self.stdout.write(self.style.SUCCESS('Időpontok létrehozva!'))