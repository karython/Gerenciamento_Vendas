# Generated migration for performance optimization
# This migration adds database indexes to improve login and session query performance

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_controle', '0013_venda_orcamento_origem'),
    ]

    operations = [
        # Add index to CNPJ field for faster lookups
        migrations.AddIndex(
            model_name='loja',
            index=models.Index(fields=['CNPJ', 'ATIVO'], name='idx_loja_cnpj_ativo'),
        ),
        # Add db_index to CNPJ field (for unique index)
        migrations.AlterField(
            model_name='loja',
            name='CNPJ',
            field=models.CharField(db_index=True, max_length=18, unique=True, verbose_name='CNPJ'),
        ),
        # Add db_index to ATIVO field for faster filtering
        migrations.AlterField(
            model_name='loja',
            name='ATIVO',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]
