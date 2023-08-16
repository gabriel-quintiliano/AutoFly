from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.expected_conditions import presence_of_element_located, new_window_is_opened, url_changes, staleness_of
from selenium.common import exceptions as exc

import time
import datetime as dt
from sys import exit

import csv
from os import linesep as os_linesep
from cryptography.fernet import Fernet

# Para verificações necessárias
from selenium.webdriver.remote.webelement import WebElement


# + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - +

# Original e funcional
mascaras = {
    '001.001.076': {'organograma': '76', 'processos': [], 'online': False},
    '001.001.211': {'organograma': '209', 'processos': [], 'online': False},
    '001.001.555': {'organograma': '555', 'processos': [], 'online': False},
    '001.001.197': {'organograma': '195', 'processos': [], 'online': False},
    '001.001.541': {'organograma': '546', 'processos': [], 'online': False},
    '001.001.569': {'organograma': '569', 'processos': [], 'online': False},
    '001.001.356': {'organograma': '358', 'processos': [], 'online': False},
    '001.001.115': {'organograma': '115', 'processos': [], 'online': False},
    '001.001.182': {'organograma': '180', 'processos': [], 'online': False},
    '001.001.360': {'organograma': '362', 'processos': [], 'online': False},
    '001.001.132': {'organograma': '132', 'processos': [], 'online': False},
    '001.001.165': {'organograma': '164', 'processos': [], 'online': False},
    '001.001.188': {'organograma': '186', 'processos': [], 'online': False},
    '001.001.355': {'organograma': '357', 'processos': [], 'online': False},
    '001.001.565': {'organograma': '565', 'processos': [], 'online': False},
    '001.001.206': {'organograma': '205', 'processos': [], 'online': False},
    '001.001.191': {'organograma': '189', 'processos': [], 'online': False},
    '001.001.164': {'organograma': '163', 'processos': [], 'online': False},
    '001.001.358': {'organograma': '360', 'processos': [], 'online': False},
    '001.001.194': {'organograma': '192', 'processos': [], 'online': False},
    '001.001.202': {'organograma': '200', 'processos': [], 'online': False},
    '001.001.163': {'organograma': '162', 'processos': [], 'online': False},
    '001.001.359': {'organograma': '361', 'processos': [], 'online': False},
    '001.001.357': {'organograma': '359', 'processos': [], 'online': False},
    '001.001.213': {'organograma': '211', 'processos': [], 'online': False},
    '001.001.079': {'organograma': '79', 'processos': [], 'online': False}
    }

# Variáveis que vão lidar com etiquetas, comp. de abertura e comp. de confirmação dos processos corrigidos
etiquetas_isoladas = list()
comp_abertura_isolados = list()
comp_confircacao_isolados = {'76': [], '209': [], '555': [], '195': [],
                      '546': [], '569': [], '358': [], '115': [],
                      '180': [], '362': [], '132': [], '164': [],
                      '186': [], '357': [], '565': [], '205': [],
                      '189': [], '163': [], '360': [], '192': [],
                      '200': [], '162': [], '361': [], '359': [],
                      '211': [], '79': []}

# Keys para serem usadas com o arquivo de dados da execução anterior
exec_file_keys = ['solicitacao', 'data_andamento', 'req_e_bef', 'geral']

# Solicitações (por código) sem etiquetas == certidões e cópias
sem_etiqueta = [
    '618', '604', '57', '27', '78', '597', '674', '203', '598', '4', '635',
    '581', '3', '636', '569', '568', '626', '685', '570', '516', '610', '643',
    '627', '5', '33', '34', '628', '66', '571', '572', '650', '573', '42',
    '35', '36', '574', '37', '50', '632', '38', '575', '578', '39', '579',
    '548', '380', '40', '634', '629', '41', '503', '676', '576', '67', '631',
    '630', '577', '68', '566', '107', '625', '106', '682', '533', '567', '105',
    '526', '280', '104'
    ]

# número de processos sem andamento serão incluídos nessa lista abaixo
sem_andamento = list()

# número de processos com andamento para um organograma que não está no dicionário 'mascaras'
# serão incluídos nessa lista abaixo
andamento_desconhecido = list()

# Feriados de 2023 para o programa saber que nesses dias não teve processos
feriados = ['01/05/2023', '08/06/2023', '09/07/2023', '15/08/2023', '07/09/2023',
            '12/10/2023', '28/10/2023', '02/11/2023', '15/11/2023', '20/11/2023',
            '25/12/2023']

str_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

# A variável abaixo vai guardar quantos relatórios de confirmação e de estiquetas foram emitidos
total_rel_etiquetas = 0
total_rel_planilhas = 0
total_rel_comp_abert = 0

"""# Essa variável vai guardar todas as opções obtidas a cada call da função get_options()
overall_options = dict()"""

# + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - +

def _initialize_global_variables():
    global hoje
    global path
    global exec_info
    global user_options
    
    hoje = dt.datetime.now(tz=dt.timezone(dt.timedelta(hours=-3), 'UTC-3'))
    path = get_options('filepaths.txt', separator=':')
    exec_info = get_options(path['execution_info'], separator=':')
    user_options = get_options('options.txt', separator=':')
    parse_password()


def parse_password():

    ps_prefix = user_options['password'][:2]
    passw = user_options['password']

    if ps_prefix == '_ ':
        key = user_options['key']
        decrypter = Fernet(key)
        user_options['password'] = decrypter.decrypt(passw[2:].encode()).decode()
        return

    key = Fernet.generate_key().decode()
    encrypter = Fernet(key)
    enc_password = '_ ' + encrypter.encrypt(passw.encode()).decode()
    write_value_for_key('./options.txt', ('key', 'password'), (key, enc_password), separator=':')


def abrir_e_logar(user: str, password: str, organograma: str):

    # Abre a página inicial do Fly Protocolo, faz o login de acordo com os argumentos 'user' e 'password' e por fim
    # seleciona o organograma de acordo com o argumento 'organograma'. Se uma das credenciais ou organograma fornecidos
    # estiver incorreto, será impressa uma mensagem explicando o erro e o programa será encerrado.

    try:
        global driver
        global wait60
        global wait10
        global nav_principal

        driver = webdriver.Chrome()
        wait60 = WebDriverWait(driver, 60)
        wait10 = WebDriverWait(driver, 10, poll_frequency=0.05)
        nav_principal = driver.window_handles[0]

    except exc.WebDriverException:
        print("""Faça o download do webdriver do Google Chrome em https://chromedriver.chromium.org/downloads de acordo com sua versão""")
        fechar_nav_e_pausar_antes_sair()
        
    driver.maximize_window()
    driver.get("https://e-gov.betha.com.br/protocolo/01038-227/login.faces")
    
    logar_fly(user, password)
    acessar_organograma(organograma)


def acessar_organograma(organograma: str) -> None:

    # Verifica se o navegador está na página de seleção de organogramas e acessa o organograma de acordo com o
    # argumento 'organograma'. Caso não exista esse organograma ou não esteja na página de seleção, será impressa
    # uma mensagem explicando o erro e será encerrada a execução do programa.

    if "selecaoorganograma.faces" in driver.current_url:

        if (organograma := find_matching_org(organograma)):
            driver.find_element(By.LINK_TEXT, organograma).click()
        else:
            print("\n\nO organograma informado não está disponível ou foi escrito de maneira incorreta.\n")
            fechar_nav_e_pausar_antes_sair()
    
    else:
        print("Parece que você não está na página de seleção de organogramas")
        fechar_nav_e_pausar_antes_sair()


def find_matching_org(organograma: str) -> str | None:

    # Verifica se o navegador está na página de seleção de organogramas e verifica se o organograma passado como
    # argumento de fato está disponível para ser selecionado. Retorna uma string contendo o texto exato do link
    # do organograma como está na página, ou, se este não foi localizado, retorna None

    organograma = organograma.upper()
    organogramas_disp = driver.find_elements(By.XPATH, "//table[@id='mainForm:organogramasCadastrados']/tbody/tr")

    for org in organogramas_disp:
        org = org.text
        if org.lstrip("0123456789-. ") == organograma:
            return org
    return None


def logar_fly(user: str, password: str) -> None:

    # Verifica se está na página de login do fly e tenta fazer o login com as credenciais fornecidas.
    # Não estando na página de login ou se uma das credenciais estiver errada será impressa uma mensagem
    # com o erro correspondente e a execução do programa será encerrada. 

    if "login.faces" in (url_login := driver.current_url):
        driver.find_element(By.ID, "login:iUsuarios").send_keys(user)
        driver.find_element(By.ID, "login:senha").send_keys(password)
        driver.find_element(By.ID, "login:btAcessar").click()
        try:
            # A linha abaixo espera por até pela url da página mudar, sim isso ocorrer imedidatamente a
            # execução do programa continua, se não, vai dar timeout e rodar o codigo do except block
            # o que ocorre é que se a url de fato não mudar significa que o login não deu certo.
            WebDriverWait(driver, 2).until(url_changes(url_login))
        except exc.TimeoutException:
                print("Alguma das informações de login fornecidas está incorreta, verifique  o arquivo 'login_fly.txt' e execute o programa novamente")
                fechar_nav_e_pausar_antes_sair()
    else:
        print("Parece que você não está na página de login do Fly Protocolo")
        fechar_nav_e_pausar_antes_sair()


def gerar_rel_processos(data: str) -> None:

    # Gera o relatório "Demonstrativo de processos" contendo os processos protocolados no dia passado
    # como argumento 'data' no formato 'dd/mm/aaaa'

    print(f"Preparando-se para gerar o demonstrativo de processos protocolados em {data}")
    
    acessar_no_menu('Relatórios', 'Demonstrativo de processos')
    
    # Finds and store in 'formulario' the WebElement in which is the report configurations
    formulario = driver.find_element(By.ID, "mainForm")

    # Finds the "Local de protocolização" input and send the value '353' for Ganha Tempo Centro
    formulario.find_element(By.ID, "mainForm:iOrganogramas").send_keys("353")

    # Finds the "Período de protocolização" input and sends values as 'from' and 'up to' dates
    de = formulario.find_element(By.ID, "mainForm:dhProtocolizacaoIni")
    de.clear()
    de.send_keys(data)
    print("DATA DATA DATA",data, '\n\n\n\n')

    ate = formulario.find_element(By.ID, "mainForm:dhProtocolizacaoFim")
    ate.clear()
    ate.send_keys(data)
    print("DATA DATA DATA",data, '\n\n\n\n')

    # Finds the "Formato de saída" possible input and selects the 'html' option
    # Actually goes directly to the webelement through its ID identification
    formulario.find_element(By.ID, "mainForm:exportType:1").click()
    
    # Finds and Clicks on the button "Emitir"
    formulario.find_element(By.ID, "mainForm:btExecRelBackground").click()
    
    print("Demonstrativo de processos emitido!\n")


def processo_online(processo: WebElement) -> bool:
    
    # Retona True se é um processo online e False caso não seja
    
    # Captura como WebElement a linha inteira do campo 'Observação' (elem 'tr' no html)
    try:
        # A linha abaixo tenta buscar no html do processo, no campo 'observação' um texto que tenha
        # 10 letras ou menos e extrair o esse texto do WebElement que foi encontrado.
        # No relatório do Fly, se não há texto na 'observação', nem vai haver uma td[2]/span depois
        # após a td com o texto 'Observação:', o que vai gerar uma exceção NoSuchElementException
        # nesse caso retornaremos False direto pelo except block
        texto_obs = processo.find_element(By.XPATH, "tbody/tr/td[span[text()='Observação:']]/following-sibling::td[2]/span[string-length(text())<=10]").text
        texto_obs = texto_obs.lower()

        # Verifica se num sistema de string e substring se tem a palavra 'online' escrita de qualquer
        # maneira razoável escrita na observação
        keyword = 'online'
        i = 0
        for letra in texto_obs:
            if keyword[i] == letra:
                i += 1 # As letras são iguais, então podemos avançar o 'i' para verificar a próxima letra
            
            # Se i for >= a length de 'online' significa que todas as letras foram encontradas nessa ordem
            # no texto de no máximo 10 letras presente na observação do processo
            if i >= len(keyword):
                return True
        
        # Se o programa chegou aqui significa que todas as letras da observação foram verificadas mas nem
        # todas as letras de 'online' foram encontradas
        return False

    except exc.NoSuchElementException:
        return False


def get_left_most_numbers_from(text: str) -> str:

    # Captura os números que aparecem em sequencia a partir da esquerda do texto, na primeira incid~encia
    # de um caracter que não seja um número, a função retorna os números que foram capturados até o momento
    
    for n, letra in enumerate(text):
        if not letra.isdigit():
            return text[:n]


def abrir_rel_e_mudar_foco() -> None:
    # Acessa a aba 'Gerenciador de relatórios' em 'Relatórios', espera por até 10 segundos o relatório mais
    # recente ficar disponível (ou seja, o botão 'exibir' aparecer), abre esse relatório e muda o foco do
    # driver para este.

    acessar_no_menu('Relatórios', 'Gerenciador de relatórios')
    link_relatorio = wait60.until(presence_of_element_located((By.XPATH, "//div[@id='mainForm:reports']/div[1]/descendant::div[@class='actions']/a[text()='Exibir']")))
    link_relatorio.click()

    wait60.until(new_window_is_opened(driver.window_handles))
    driver.switch_to.window(driver.window_handles[-1])


def acessar_no_menu(*menus: str) -> None:

    # Acessas os menus e submenus na ordem em que foram passados na chamada da função
    # Se não for possível localizar qualquer um dos menus descritos, será executado o except block
    # e impressa uma mensagem explicando esse erro

    # Como menus inicialmente é um tuple, abaixo estramos transformando este em uma lista
    # para que os itens sejam indexáveis
    menus = list(menus)

    # Como não tem um link com o exato texto 'Gestão de protocolos', se tal for passado como
    # argumento, teremos que capturar esse elemento de outra maneira para então poder
    # acessar este, também, como não há opções nesse caso só clicamos e a função acaba
    if menus[0] == 'Gestão de protocolos':
        home = driver.find_element(By.XPATH, "//span[@id='fHeader:sHeader:fullMenu']//ul[@id='nav']//li[@class='icons first']//a[img[@title='Gestão de protocolos']]")
        home.click()
        return
    
    while True:
        try:
            # Extrai do html o WebElement que representa o menu superior principal descrito
            xpath_exp = f"//span[@id='fHeader:sHeader:fullMenu']//ul[@id='nav']//li[a[text()='{menus[0]}']]"
            aba_especifica = driver.find_element(By.XPATH, xpath_exp)
            
            # Esse loop vai iterar por cada um dos menus e submenus passados como argumentos e acessar cada
            # um na ordem em que foram passados
            for n, submenu in enumerate(menus):
                elem = aba_especifica.find_element(By.LINK_TEXT, submenu)
                
                # Eu não tenho a mínima ideia do porque quando essa função é chamada como
                # acessar_no_menu('Relatórios', 'Gerenciais', 'Estornos de processo', 'Encerrados')
                # só funciona com essas duas linhas de código abaixo, não tenho a mínima ideia
                # se tirar qualquer uma das duas dá erros. Deve ter a ver com o itme encerrados
                # estar lá na pqp embaixo da tela. RESOLVER DPS EM ALGUM MOMENTO
                elem.screenshot(f"C:/Users/gabri/OneDrive/Área de Trabalho/step{n}.png")
                driver.execute_script("arguments[0].scrollIntoView();", elem)
        
                elem.click()
        
            return
            
        except exc.ElementClickInterceptedException:
            fechar_notificacao()
        
        except exc.ElementNotInteractableException:
            # Vai ser no caso de já ter fechado uma vez e desaparecido ao tentarmos interagir
            pass

        except exc.NoSuchElementException:
            print(f"""Não foi possível localizar a opição '{submenu}'\nVerifique a ortografia da palavra, se a opição realmente existe e se esta descrina na ordem correta""")
            fechar_nav_e_pausar_antes_sair()


def fechar_notificacao():

    # Vai achar o botão ignorar e clicar nele até desaparecer.
    # Se não achar o botão (NoSuchElementException) ou achar e tentar clicar mas este já tiver
    # desaparecido (StaleElementReferenceException) vai entrar no except e finalizar a função.
    # ElementNotInteractableException vai ser no caso de já ter fechado uma vez, reaparecer e ao tentar
    # clicar ter desaparecido denovo, o elemento ainda está no html mas não é mais clicavel

    try:
        ignorar = driver.find_element(By.XPATH, "//div[@id='tooltipNotifications']/div/a[@title='Fecha esta janela']")
        while True:
            ignorar.click()
    except (exc.NoSuchElementException, exc.StaleElementReferenceException, exc.ElementNotInteractableException):
        pass

# Essa função vai ser usada quando tiver algum tipo de aviso que aparece na tela para confirmar que
# o relatório está sendo gerado, para então retornar True se esse relatório apareceu (e deu certo o
# click no botão emitir) ou retonar False se não apareceu
def emitido_com_sucesso():
    try:
        # Esses 0.2 segundos são importantes para dar tempo do aviso carregar, se for mesmo carregar...
        time.sleep(0.2)
        driver.find_element(By.XPATH, "//div[@id='mainForm:master:messageSection:info' and text()]/a[text()='clique aqui']")
        return True
    except exc.NoSuchElementException:
        return False


def preencher_e_emitir(field: str, text: str, button: str =None, press_enter: bool =True, notice: bool =False, notification: bool =False) -> None:

    # Essa é uma função que eu tentei fazer de um jeito 'generico' para poder ser usada no preenchimento de
    # qualquer formulário dentro do Fly, é só configurar direto cada parametro no momento de chamada da função
    # field = nome (exato) do campo que você quer preencher (não incluir ':')
    # text = texto que você quer preencher em 'field'
    # button = nome do botão que deverá ser clicado depois de preencher text em field, ex: 'Emitir', 'Consultar'
    #          Por default nenhum botão está definido, ao invés disso envia-se 'ENTER' para 'field'
    #          (como se estivesse precionando esse botão físico no teclado)
    # press_enter = indica se a função deve ou não 'precionar ENTER' no field após escever o texto neste.
    #               Por default, a função 'preciona' ENTER. OBS: Se for passado um valor para 'button',
    #               press_enter vai necessáriamente ser False.
    # notice = indica se a função terá ou não que lidar com algum aviso de confirmação de que o relatório foi
    #          emitido com sucesso e está sendo carregado
    # notification = indica se a função terá ou não que lidar a janela de notificações sobre relatórios prontos 
    
    # Obtém o id de 'field' no html
    while True:
        try:
            field_id = driver.find_element(By.XPATH, f"//label[text()='{field}:']").get_attribute("for")
            break
        except exc.StaleElementReferenceException:
            pass
        except exc.NoSuchElementException:
            print(f"Não foi possível encontrar um field escrito exatamente como: '{field}' na página, verifique a ortografia")
            fechar_nav_e_pausar_antes_sair()

    # Aqui tem um while True para que a cada exceçao que for capturada pelo try/except block, depois de
    # esta ser manejada, volte a ser executado o mesmo código desde o início. Esse loop só vai para quando
    # for executado por completo (até o break) e assim, tendo a certeza que houve sucesso no preenchimento
    # do campo conforme especificado
    while True:
        try:
            _field = driver.find_element(By.ID, field_id) # Captura o field
            _field.clear() # Só pra garantir, limpa o field

            # ajuda muito esperar esses 0.2 segundos para não escrever nada no field errado acidentalmente
            time.sleep(0.2)
            _field.send_keys(text) # Escreve o text no field


            if button:
                _button = driver.find_element(By.XPATH, f"//input[@value='{button}' and @type='button']")
                _button.click()
                
                if notice:
                    if not emitido_com_sucesso():
                        _button.click()
            else: # se não tiver um botão definido, a função 'pressiona' ENTER
                _field.send_keys(Keys.ENTER)
            
            break # all done
            
        except exc.StaleElementReferenceException:
            pass # Assim não dá erro e voltamos para o inicio do loop

        except exc.ElementClickInterceptedException:
            if notification:
                fechar_notificacao()

        except (exc.ElementNotInteractableException, exc.InvalidElementStateException):
            driver.refresh()
            return False
        
        except exc.NoSuchElementException:
            if button:
                print(f"Não foi possível localizar o(s) elemento(s) com '{field}' e/ou '{button}'")
            else:
                print(f"Não foi possível localizar o elemento com '{field}'")
            fechar_nav_e_pausar_antes_sair()


# FUNÇÃO REFATORADA
def emitir_etiquetas():

    print('Preparando-se para emitir etiquetas...')

    acessar_no_menu('Relatórios', 'Etiquetas')

    # muda o modelo para "modelo com beneficiário"
    Select(driver.find_element(By.ID, "mainForm:iEtiquetas")).select_by_visible_text("Mod com Beneficiario")

    fonte_processos = [etiquetas_isoladas] if etiquetas_isoladas else mascaras.values()

    for processos in fonte_processos:
        
        # Se etiquetas isoladas é um valor falsy, significa que não estamos lidando com processos
        # corrigidos, assim processos (acima) é um valor de mascaras, o qual por sua vez é um dicionário
        # com a key 'processos' para o números dos processos de determinado organograma.
        if not etiquetas_isoladas:
            processos = processos['processos']

        # checa se tem algum processo dentro da lista, se não tiver nem acessa a lista
        # quando não no modo de processos corrigidos pode acontecer de não ter nenhum processo
        # para determinado organograma, por isso é necessária a verificação
        if processos:
            
            # se não tiver a func iter(), ocorrerá apenas 1 iteração considerando slice como
            # a lista inteira de chunks ao invés de acessar 1 chunk de cada vez.
            # Aparentemente, com iterables, a função/dunder method __iter__() chamado por
            # padrão, mas com funções não, mesmo que retornem 1 iterable no final.
            for chunk in iter(slice_in_chunks(processos, 23)):

                input_formatado = ','.join(chunk)
                
                # preenche 'input_formatado' no campo 'Número do processo'
                preencher_e_emitir("Número do processo", input_formatado, button="Emitir", notification=True, notice=True)
                global total_rel_etiquetas
                total_rel_etiquetas += 1

    print("Etiquetas emitidas!\n")


def emitir_comprovantes_de_confirmação(data: str):

    # Emite os comprovante de confirmação dos processos de acordo 'data' no formato 'dd/mm/aaaa'

    print('Preparando-se para emitir os comprovates de confirmação...')
    
    global total_rel_planilhas # para a função pegar a variável global ao invés de criar uma local
    acessar_no_menu("Relatórios", "Comprovante de confirmação")

    # Seleciona "Gerar comprovantes por" --> "Por processos"
    Select(driver.find_element(By.ID, "mainForm:tipo")).select_by_visible_text("Por processos")
    
    # Para dar tempo de carregar as opções descritas abaixo depois de mudar o select acima
    time.sleep(0.3)

    # Data dos andamentos
    de = driver.find_element(By.ID, "mainForm:dhAndamentosIni")
    ate = driver.find_element(By.ID, "mainForm:dhAndamentosFim")
    
    de.send_keys(data)
    ate.send_keys(data)

    # Itera por cada uma das mascaras de organograma
    for dados in mascaras.values():
        
        # Se tiver qualquer tipo de processo nesse organograma, será emitido o comprovante de confirmação
        # desse organograma específico
        if dados['processos'] or dados['online']:

            organograma = dados['organograma']
            preencher_e_emitir("Destinado à", organograma, button="Emitir", notice=True, notification=True)
            total_rel_planilhas += 1

    print("Todos os comprovantes de confirmação foram emitidos!\n")


def obter_login():
    try:
        with open('login_fly.txt', 'r') as fp:
            login = csv.DictReader(fp)
            return(next(login))
    except FileNotFoundError:
        print("O arquivo 'login_fly.txt' não foi encontrado, este deve estar na mesma pasta que o programa.")
        pausar_antes_de_sair()
    except OSError:
        print("Aconteceu um erro ao abrir o arquivo 'login_fly.txt', rode o programa novamente.")
        pausar_antes_de_sair()


def demonstrar_processos_sem_andamento(msg: str ="\nProcessos sem andamento:"):
    if sem_andamento:
        print(msg)
        for processo in sem_andamento:
            print(processo)


def demonstrar_processos_com_andamento_incomum(msg: str ="\nProcessos com andamento 'incomum':"):
    if andamento_desconhecido:
        print(msg)
        for processo in andamento_desconhecido:
            print(processo)


def wait_update_after_action_in(element: WebElement):
    while True:
        try:
            _ = element.tag_name # tag_name porque todo WebElement tem esse atributo
            time.sleep(0.05) # Para dar um intervalo e diminuir a quantidade de calls da função
        except exc.StaleElementReferenceException:
            return


def go_to_page(page_index):
    
    x = 1
    while True:
        try:
            link = driver.find_element(By.XPATH, f"//div[@id='mainForm:reportsPaginationPanel']/descendant::a[text()='{page_index}']")
            already_in_page = "active dontCancelClick" == link.get_attribute('class')
    
            if not already_in_page:
                link.click()
                already_in_page = "active dontCancelClick" == link.get_attribute('class')
            
            if already_in_page:
                return
            
        except exc.StaleElementReferenceException:
            # Essa exceção deve ter sido raised ao tentar clicar no link, então vamos tentar denovo
            pass
        except exc.NoSuchElementException:
            # Essa exceção deve ter acontecido ao tentar capturar o link do botão da pagina conforme
            # page_index, mas esta não estar aparecendo na barra de navegação. Nesse caso então,
            # o programa vai buscar entender se temos que voltar ou avançar na barra de navegação
            # para encontrar o botão da página desejada.
            if find_page(page_index):
                return
            else:
                print(f'Por algum motivo não foi possível localizar a página ')
                fechar_nav_e_pausar_antes_sair()
        except exc.UnexpectedAlertPresentException:
            print(f'Apareceu Alerta - page_index = {page_index}')
            pausar_antes_de_sair()
        
        x += 1


def find_page(target_page: int) -> bool:

    if target_page < 0:
        return False

    while True:
        try:
            current_page = driver.find_element(By.XPATH, f"//div[@id='mainForm:reportsPaginationPanel']/descendant::a[@class='active dontCancelClick']")
            current_page = int(current_page.get_attribute('text'))
    
            clicks_needed = target_page - current_page
        
            if clicks_needed > 0:
                button_class = 'next'
            elif clicks_needed < 0:
                button_class = 'prior'
            else:
                return True # Já está na target page
            
            clicks_needed = abs(clicks_needed)
            clicks_performed = 0
            
            while clicks_performed < clicks_needed:
                try:
                    botao = driver.find_element(By.XPATH, f"//div[@id='mainForm:reportsPaginationPanel']/descendant::a[@class='{button_class}']")
                    botao.click()
                    wait10.until(staleness_of(botao))
                    clicks_performed += 1
                except exc.StaleElementReferenceException:
                    # Não deve haver mais exceções como esta devido a função wait_update_after_action_in(botao)
                    # que vai garantir nesse caso que o código só continue a execução depois do html ser atualizado
                    # de acordo com a ação performada (igual o nome da função). Ainda há a possibilidade de ocorrer
                    # essa execeção em 'botao.click()' mas é bem improvável visto que são linhas seguidas a serem
                    # executadas quase que no mesmo instante. Antes de empregar a função, o que causava essa exceção
                    # era que o programa é mais rápido que a atualização do html na página do navegador, assim,
                    # executava o clique, computava este (com clicks_performed) e dava tempo de o loop reiniciar e
                    # buscar pelo botão ('next' ou 'prior') novamente antes do html atualizar, até que por fim,
                    # terminava de carregar a atualização e na próxima ao tentar clicar esse botão (de antes da
                    # atualização) a exceção era raised.
                    pass
                except exc.NoSuchElementException:
                    # Pelo mesmo motivo esposto para a exceção acima, é improvável que o método find_element seja
                    # executado quando a página ainda estiver atualizando e não seja possível localizar o botão
                    # específico que precisamos. Portanto, vou levar em consideração que essa exceção vai ocorrer
                    # somente quando realmente o botão não estiver disponível devido  termos chegado ao fim da
                    # barra de navegação, mas mesmo assim, só pra confirmar verificamos pelo botão com a class
                    # 'nextd' para a qual o botão next é alterado quando fica inativo.
                    try:
                        botao = driver.find_element(By.XPATH, f"//div[@id='mainForm:reportsPaginationPanel']/descendant::a[@class='nextd']")
                    except exc.NoSuchElementException:
                        pass
                    return False
        except exc.StaleElementReferenceException:
            pass


def get_items_per_page():
    while True:
        try:
            items_per_page = driver.find_element(By.XPATH, "//div/select[@id='mainForm:nritems-top']/option[@selected]")
            return int(items_per_page.text)
        except (exc.StaleElementReferenceException, exc.NoSuchElementException):
            pass


def construir_dict(inicio, fim):
    
    # This function constructs a dictionary that maps (according to xpath counting standard) reports
    # to the pages they're in, acording to an range (inicio to fim) which represents the position
    # from the first report uninterrupted ultil the last report we want to sort.

    dicio = dict()

    # reps_per_page is the default quantity of reports displayed in the page
    reps_per_page = get_items_per_page()
            
    # início - 1 é para 'corrigir' a o início da contagem para 0 visto que os argumentos
    # ínicio e fim são ordinais que representam a posição processo na página, assim,
    # contagem iniciada de 1 igual no xpath.

    for x in range(inicio - 1, fim):
        try:
            # dentro das expressões abaixo, o +1 é um offset para ajustar a contagem
            # novamente para começando do 1, igual no xpath
            dicio[x // reps_per_page + 1].append(x % reps_per_page + 1)
        except KeyError:
            dicio[x // reps_per_page + 1] = [x % reps_per_page + 1]
    
    return dicio


def abrir_relatorios_emitidos():
    acessar_no_menu('Relatórios', 'Gerenciador de relatórios')

    total_reports = total_rel_etiquetas + total_rel_planilhas + total_rel_comp_abert

    if total_reports > 0:
        reports_map = construir_dict(1, total_reports)
        print(reports_map)
        handle_reports(reports_map)

    else:
        print('Não existem relatórios para serem emitidos')


def handle_reports(rto):

    while True:
        aguardando = dict()

        for page, reports in rto.items():
            go_to_page(page)
            for report in reports:
                if not handle_report(report):
                    try:
                        if aguardando[page]:
                            aguardando[page].append(report)
                    except KeyError:
                        aguardando[page] = [report]
        
        if not aguardando:
            return
        
        rto = aguardando
        print(aguardando)
        time.sleep(1)


def handle_report(report_index):
    
    initial_num_window_handles = len(driver.window_handles)

    while True:
        try:
            link = driver.find_element(By.XPATH, f"//div[@id='mainForm:reports']/div[{report_index}]/descendant::div[@class='actions']/a")
            link_text = link.text
    
            if link_text == 'Exibir':
                while True:
                    try:
                        link = driver.find_element(By.XPATH, f"//div[@id='mainForm:reports']/div[{report_index}]/descendant::div[@class='actions']/a")
                        link.click()
                        
                        # Antes tinha um while True aqui, que esperaria até abrir mais uma janela, mas as
                        # vezes bugava e eu não sei se o click() que não dava certo ou o que mas nunca abria
                        # essa nova janela e o loop nunca se encerrava. Agora, verificamos essa condição 5x
                        # apenas (durante 1 segundo portanto), se não clicamos denovo no mesmo relatório.
                        for i in range(5):
                            if not len(driver.window_handles) > initial_num_window_handles:
                                time.sleep(0.2)
                            else:
                                return True

                    except Exception as e:
                        print(e)
                        pass
            
            # Se a condição abaixo for True, significa que esse relatório ainda está carregando, portanto
            # como não poderemos manejá-lo agora, retornaremos False (função malsucedida)
            elif link_text == 'cancelar':
                return False
            
            # Se o programa chegou até essa linha de código, ou o relatório foi aberto (clicando em 'Exibir')
            # ou este é um relatório sem linhas geradas ('link_text' == inválido)
            # qualquer dos casos que seja, a função foi bem sucedida e o relatório manejado
            return True
        
        except (exc.StaleElementReferenceException, exc.NoSuchElementException):
            pass


def esperar_usuario_e_sair() -> None:
    # Essa funç~çao vai ser chamada depois de todo o processo de login, gerar relatórios
    # extração e preenchimento dos números de processo. Vai esperar até o usuário terminar de
    # imprimir cada um dos relatórios gerados para fechar o navegador e encerrar o programa
    # quando o usuário fechar todos os relatórios e só houver o fly protocolo aberto

    while len(driver.window_handles) > 1 and driver.window_handles[0] == nav_principal:
        time.sleep(1)
    fechar_nav_e_pausar_antes_sair()


def fechar_nav_e_pausar_antes_sair():
    driver.quit()
    _ = input("\nPressione ENTER para sair...")
    exit()

def pausar_antes_de_sair():
    _ = input("\nPressione ENTER para sair...")
    exit()


def write_value_for_key(filepath, keys, values, separator=','):

    # makes sure that keys and values are the same type
    if not (type(keys) is type(values)):
        print("Ambos os argumentos 'keys' e 'values' de write_value_for_key() tem que ser do mesmo tipo, str ou list (com a mesma length)")
    
    # As keys and values are from the same type, if it's not a tuple or list (hence a str), this
    # conditional turns this argument values into a tuple to ensure expected behavior from zip() below
    elif not (isinstance(keys, tuple) or isinstance(keys, list)):
        keys = (keys,)
        values = (values,)

    try:
        with open(filepath, 'r+b') as fp:
            
            cur_fpi = fp.tell()
            fp.seek(0,2)
            file_end = fp.tell()
            fp.seek(cur_fpi)

            for key, value in zip(keys, values):
                if (cur_fpi := set_fpi(fp, key, separator)) != file_end:

                    rest_of_file = parse_remaining_text(fp.read())
                    fp.seek(cur_fpi)

                    # Para melhorar a leitura, eu incluí um espaço e quebra de linha a serem escritos
                    # junto com o 'value' passado pelo usuário.
                    fp.write(f' {value}{os_linesep}'.encode())
                    
                    # Se já não tiver nada no resto do arquivo, não tem oque escrever
                    if rest_of_file:
                        fp.truncate()
                        fp.write(rest_of_file)
                    
                    fp.seek(0)
                else:
                    print(f"Não foi possível localizar a key '{key}' com o separator '{separator}'")
                    exit()
        
    except FileNotFoundError:
        print(f"O arquivo '{filepath}' não foi encontrado, este deve estar na mesma pasta que o programa.")
        exit()
    except OSError:
        print(f"Aconteceu um erro ao abrir o arquivo '{filepath}', rode o programa novamente.")
        exit()


def parse_remaining_text(b_text):
    
    if not isinstance(b_text, bytes):
        bytes.encode()

    os_linesep_len = len(os_linesep)
    _os_linesep = os_linesep.encode()
    start = 0

    # O loop vai iterar até acharmos a quebra de linha '\n', '\r' ou '\r\n'
    while True:
        slice =  b_text[start : start + os_linesep_len]
        
        if slice == _os_linesep:
            # retorna um slice que começa logo após encontrar o linesep
            return b_text[start + os_linesep_len: ]
        
        # mesmo caso da função original, dps anotar melhor
        if len(slice) < os_linesep_len:
            return b''
    
        start += 1


def set_fpi(file, key: str, separator: str = ',', reference: str = '>') -> bool:
        # Returns True if fpi is set to right after specified 'key' argument separator
        # if it reaches the end of file or doesn't find the key, it returns False
        
        key = (key + separator).encode()

        key_length = len(key)
        possible_key = ''
        
        # While end of file isn't reached
        while (char_read := file.read(1)) != b'':

            if char_read == key[:1]:
                possible_key = char_read + file.read(key_length - 1)

                if possible_key == key:
                    if reference == '<':
                        file.seek(-key_length, 1)
                    break

                file.seek(-(key_length - 1), 1)

        return file.tell()


def get_options(filepath, separator: str = ',') -> None:
    
    if len(separator) > 1:
        print("o keyword argument 'separator' não pode ter mais de 1 characterer, corrija seu arquivo")
        exit()
    
    try:
        with open(filepath, 'rb') as fp:
            options = _create_custom_dict(fp, separator)

            return options
        
    except FileNotFoundError:
        print(f"O arquivo '{filepath}' não foi encontrado, este deve estar na mesma pasta que o programa.")
        exit()
    except OSError:
        print(f"Aconteceu um erro ao abrir o arquivo '{filepath}', rode o programa novamente.")
        exit()


def _create_custom_dict(file, separator) -> dict:
    
    dicio = dict()
    linesep_len = len(os_linesep)
    
    while (line := file.readline()):
        # reads the line, extracts all the type bytes objects (which are the chars) decodes the bytes
        # to text and lastly, it splits the recovered line into a list of values according to the separator
        line = line.decode()
        
        i = 0
        while line[i] != separator and line[i:i+linesep_len] != os_linesep:
            i += 1
        
        if line[i:i+linesep_len] != os_linesep:
            key = line[:i]
            value = line[i+1:].strip()

            dicio[key] = value
    
    return dicio


def gerar_data_referencia():
    
    global ref_date

    try:
        ref_date = user_options["reference_date"]
        if (ref_date):
            return ref_date
    except KeyError:
        pass
    
    ref_date = hoje
    
    if hoje.hour < 14:
        ref_date = hoje - dt.timedelta(1)
        while ref_date.weekday() >=5 or ref_date.strftime('%d/%m/%Y') in feriados:
            ref_date -= dt.timedelta(1)
    
    ref_date = ref_date.strftime('%d/%m/%Y')

    print("ref_date ref_date ref_date ref_date", ref_date)

    return ref_date

def register_excecution_info():

    keys = (
        'last_execution',
        'by_user',
        'reference_date',
        'emitir_etiquetas',
        'emitir_planilhas'
    )

    values = (
        hoje.strftime('%d/%m/%Y %H:%M'),
        user_options['user'],
        ref_date,
        user_options['emitir_etiquetas'],
        user_options['emitir_planilhas']
    )

    write_value_for_key(path['execution_info'], keys, values, separator=':')


def verificar_se_ja_foi_emitido():

    if ref_date == exec_info['reference_date']:
        print(f"\nO programa já foi executado em {exec_info['last_execution']}\nPara processos do dia {exec_info['reference_date']}\nPor '{exec_info['by_user']}'\n\nVerifique se relatórios emitidos já foram impressos.")
        while True:
            resposta = input(f"Deseja continuar com a execução do programa[s/n]? ").lower()
            print(resposta)
            if resposta == 's':
                return
            elif resposta == 'n':
                exit()


def get_continuous_key_index(file, ckey: str, separator=',') -> int:
    
    initial_fpi = file.tell()
    ckey_index = 0

    while (line := file.readline()):
        # reads the line, extracts all the type bytes objects (which are the chars) decodes the bytes
        # to text and lastly, it splits the recovered line into a list of values according to the separator
        
        i = 0
        while line[i:i+1] != separator:
            i += 1
        
        key = line[:i]

        if key == ckey:
            file.seek(initial_fpi)
            return ckey_index
        
        ckey_index += 1
    
    file.seek(initial_fpi)
    return None


# FUNÇÕES MAIS RECENTES FEITAS - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class Queue(list):

    def __init__(self, keys: list[str]) -> None:
        super().__init__(keys)
        self.keys = keys
        self._i = 0
        self.cur_key = keys[0]
    
    def go_to_next_key(self):
        self._i = (self._i + 1) % len(self.keys)
        self.cur_key = self.keys[self._i]
        return self.cur_key
    
    @property
    def following_key(self):
        return self.keys[(self._i + 1) % len(self.keys)]
    
    def append(self, __object) -> None:
        self.keys.append(__object)
        return super().append(__object)


def montar_dict(file, keys: Queue, separator: str) -> dict | None:
    
    values_map = dict()
    final_dict = dict()

    for _ in range(len(keys)):
        v_start = set_fpi(file, keys.cur_key, separator, '>')
        v_end = set_fpi(file, keys.following_key, separator, '<')

        v_len = v_end - v_start

        values_map[keys.cur_key] = (v_start, v_len)
        keys.go_to_next_key()
    
    for key,(v_start, v_len) in values_map.items():
        file.seek(v_start)
        value = file.read(v_len)
        final_dict[key] = value.decode()

    if final_dict[keys.cur_key]:
        return final_dict
    
    return None


def get_all_reports_info_from(filepath, keys: list[str], separator=',') -> list[dict]:
    
    reports_info = list()
    keys = Queue(keys)
    
    with open(filepath, 'rb') as fp:
        while (report := montar_dict(fp, keys, separator)):
            reports_info.append(report)
    
    if len(reports_info) > 1:
        return reports_info
    
    return reports_info[0]

# This can only be used with a file that's already opened in a mode that allows reading in binary
# if the file is closed and reopened, the call for this function will return the first report again
def get_next_report_info_from(file, keys: list[str], separator=',') -> dict:
    
    keys = Queue(keys)
    report_info = montar_dict(file, keys, separator)
    
    return report_info


# - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - +
# Nova versão de abrir_rel_e_extrair_processos()

def abrir_rel_e_extrair_processos(corrigidos: bool = False) -> None:

    abrir_rel_e_mudar_foco()

    # Se estivermos lidando com processos corrigidos abrimos no modo de leitura
    # se não, no modo de escrita, ambos como binário.
    open_mode = 'rb' if corrigidos else 'wb'

    total_protocolos = driver.find_element(By.XPATH, "//tr[td/span[text()='Total de processos:']]/descendant::span[2]").text
    total_protocolos = int(total_protocolos)
    report_index = 1

    with open('info_processos.txt', open_mode) as fp:
        while report_index <= total_protocolos:
            try:
                processo = driver.find_element(By.XPATH, f"//table/descendant::table[descendant::tr[td/span[text()='Número do processo:'] and td/span[string-length(text())=12]]][{report_index}]")
                info = extract_info_from_report(processo)
                
                if not corrigidos:
                    store_info_and_write_to_file(fp, info)
                else:
                    store_info_and_compare(fp, info)
    
            except exc.NoSuchElementException:
                pass

            report_index += 1
    
    # Agora que já extrairmos e organizamos os processos de acordo, voltamos o foco para a janela principal
    driver.switch_to.window(driver.window_handles[0])
    print("Todos os processos foram extraídos!")


def store_info_and_write_to_file(file, report: dict) -> None:

    rep_number = report['numero']
    rep_masc = report['mascara']

    if not rep_masc:
        sem_andamento.append(rep_number)

    else:
        if not report['online']:
            if report['solicitacao'] not in sem_etiqueta:
                try:
                    mascaras[rep_masc]['processos'].append(rep_number)
                except KeyError:
                    andamento_desconhecido.append(rep_number)
        else:
            mascaras[rep_masc]['online'] = True


def store_info_and_compare(file, report: dict) -> None:
    
    rep_masc = report['mascara']
    rep_number = report['numero']

    c_abert, etiq, c_confirm = False, False, False
    
    # Se foi protocolado depois da execução do programa normal 'automatizacao_fly'
    # não vai ter info nenhuma em 'info_processos.txt' então sabemos que tem que
    # imprimir tudo de qualquer jeito.
    original_info = get_next_report_info_from(file, exec_file_keys, ':')

    if not original_info or report['solicitacao'] != original_info["solicitacao"]:
        c_abert, etiq, c_confirm = True, True, True

    else:
        if report['data_andamento'] != original_info["data_andamento"]:
            etiq, c_confirm = True, True
    
        if report['req_e_bef'] != original_info["req_e_bef"]:
            c_abert, etiq = True, True
    
        if len(report['geral']) != len(original_info["geral"]):
            if report['geral'] != original_info["geral"]:
                c_abert, c_confirm = True, True
    
    if c_abert:
        comp_abertura_isolados.append(rep_number)

    if etiq:
        etiquetas_isoladas.append(rep_number)

    if c_confirm:
        if rep_masc:
            try:
                rep_org = mascaras[rep_masc]['organograma']
                comp_confircacao_isolados[rep_org].append(rep_number)
            except KeyError:
                andamento_desconhecido.append(rep_number)
        else:
            sem_andamento.append(rep_number)


# Extrai do processo com o index informado e retorna um dicionário contendo as chaves
# solicitacao, numero, online, req_e_bef, geral, mascara e data_andamento. Cada uma
# dessas tem uma string como valor (com a info sugerida pela chave) com exceção de
# 'online' que tem um valor boolean, a a info não puder ser recuperada, o valor da
# chave correspondente será '' (string vazia).
def extract_info_from_report(processo: WebElement) -> dict:
    
    info_dict = dict()
    solicitacao = processo.find_element(By.XPATH, "tbody/tr/td[span[text()='Solicitação:']]/following-sibling::td/span").text
    info_dict["solicitacao"] = get_left_most_numbers_from(solicitacao)
    
    info_dict["numero"] = processo.find_element(By.XPATH, "tbody/tr/td[span[text()='Número do processo:']]/following-sibling::td/span[string-length(text())=12 and contains(text(), '/202')]").text.lstrip('0')
    info_dict['online'] = False if not processo_online(processo) else True
    
    try:
        info_dict['mascara'] = processo.find_element(By.XPATH, "tbody/tr[td/span[text()='Máscara']]/following-sibling::tr[3]/td[2]/span[contains(text(), '001.')]").text
        info_dict["data_andamento"] = processo.find_element(By.XPATH, "descendant::tr[td/span[text()='Organograma']]/following-sibling::tr[5]/td/span").text

    except exc.NoSuchElementException:
        info_dict["data_andamento"] = ''
        info_dict['mascara'] = ''

    return info_dict


def get_field_values(report, fields) -> str:

    if not isinstance(fields, list):
        fields = [fields]
    
    values = ''
    
    for field in fields:
        # Ainda tem vários campos que configuram exceções, ou no caso de não ter uma valor disponível
        # e o xpath retorna um outro então, ou de não tem mas ele acha um span vazio
        field = field[0].upper() + field[1:] # se a pessoa escrever tudo minúsculo

        try:
            xpath_expression = f"descendant::tr/td[span[contains(text(),'{field}:')]]/following-sibling::td[2]/span"
            values += report.find_element(By.XPATH, xpath_expression).text
        except exc.NoSuchElementException:
            values += ''

    return values


def write_info_to_file(file, keys, values, separator: str = ','):

    if not (isinstance(keys, tuple) or isinstance(keys, list)):
        keys = [keys]

    if not (isinstance(values, tuple) or isinstance(values, list)):
        values = [values]

    for key, value in zip(keys, values):
        value_to_be_written = (key + separator + value).encode()
        file.write(value_to_be_written)
    

def slice_in_chunks(iterable, c_len) -> list:

    # A lógica por trás da expressão abaixo é utilizar o operador de parte inteira da divisão
    # para possibilitar uma espécie de hashing de ranges de números em um único inteiro, que
    # nesse caso vai ser a quantidade de chunks em que dividiremos o iterable.
    # Assim, por exemplo sendo c_len = 20, ou seja, para cada chunk ter no máximo 20 elementos
    # se a length do iterable for 48, sabemos que haverá um total de 3 chunks (20, 20 e 8)
    # (48 - 1) // 20 + 1 == 47 // 20 + 1 == 2(.35) + 1 == 3 chunks
    # ex2: (20 - 1) // 20 + 1 == 19 // 20 + 1 == 0(.95) + 1 == 1 chunk
    # ex3: (21 - 1) // 20 + 1 == 20 // 20 + 1 == 1 + 1 == 2 chunks
    chunks_num = (len(iterable) - 1) // c_len + 1

    chunks = list()
    start = 0

    for i in range(chunks_num):
        start = i*c_len
        end = start + c_len
        chunk = iterable[start:end]

        chunks.append(chunk)
    
    return chunks

# This call happens right here in the end to ensure it already has known all the other
# functions it might need to use...
_initialize_global_variables()