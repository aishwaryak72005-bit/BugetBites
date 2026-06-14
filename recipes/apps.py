from django.apps import AppConfig


class RecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'

    def ready(self):
        import os
        import sys
        # Automatically run migrations on startup (works on Render too)
        if not any(cmd in sys.argv for cmd in ['makemigrations', 'migrate', 'collectstatic']):
            if 'runserver' not in sys.argv or os.environ.get('RUN_MAIN') == 'true':
                from django.core.management import call_command
                try:
                    call_command('makemigrations', 'recipes')
                    call_command('migrate')
                except Exception as e:
                    print(f"Startup migrations failed: {e}")
