import auto_fly_experimental as af

def main():
    
    data = af.gerar_data_referencia()
    options = af.user_options
    # af.exit()

    if options['verificar_execucao_anterior'].lower() == 's':
        af.verificar_se_ja_foi_emitido()

    af.abrir_e_logar(options['user'], options['password'], options['organograma'])
    
    af.gerar_rel_processos(data)
    af.abrir_rel_e_extrair_processos()

    if options['emitir_etiquetas'].lower() == 's':
        af.emitir_etiquetas()

    if options['emitir_planilhas'].lower() == 's':
        af.emitir_comprovantes_de_confirmação(data)
    
    af.demonstrar_processos_sem_andamento()
    af.demonstrar_processos_com_andamento_incomum()

    if options['abrir_relatorios'].lower() == 's':
        af.abrir_relatorios_emitidos()
    else:
        af.acessar_no_menu('Relatórios', 'Gerenciador de relatórios')
    
    if options['armazenar_info_execucao'].lower() == 's':
        af.register_excecution_info()
    
    af.esperar_usuario_e_sair()


if __name__ == '__main__':
    main()