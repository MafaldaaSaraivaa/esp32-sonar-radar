# ESP32-sonar-radar

Radar de proximidade com ESP32, sensor ultrassónico HC-SR04 e servo motor SG90 — varrimento angular com medição de distância, output série, e visualização em tempo real tipo radar.

## Objetivo

Este projeto dá continuidade à exploração de microcontroladores e sensores iniciada com a [estação meteorológica], desta vez combinando um atuador (servo) com um sensor de distância para simular o funcionamento de um radar.

O objetivo desta primeira fase foi:

1. Controlar um servo motor SG90 para varrer um intervalo de ângulos (0°–180°, em vaivém).
2. Em cada ângulo, medir a distância a um obstáculo com um sensor ultrassónico HC-SR04.
3. Enviar os pares `ângulo,distância` pela porta série, para depois serem lidos e visualizados num script Python em forma de radar (gráfico polar).

## Componentes utilizados

* ESP32 (NodeMCU-32S)
* Sensor ultrassónico HC-SR04
* Micro servo motor SG90
* Breadboard e fios de ligação

## Estrutura do repositório

* `Sonar Radar/` — projeto PlatformIO (firmware C++ do ESP32)
* `Dashboard-scripts/ler_serial.py` — script que lê a porta série e faz parse dos pares ângulo/distância
* `Dashboard-scripts/visualizar_radar.py` — script que desenha o radar em tempo real (gráfico polar)

## Como correr

1. Abrir o projeto `Sonar Radar/` no VSCode com a extensão PlatformIO.

2. Criar um ficheiro `src/secrets.h` (não incluído no repositório por segurança) com: 
	#define WIFI_SSID "o_teu_ssid"
	#define WIFI_PASSWORD "a_tua_password"

3. Adicionar a dependência da biblioteca do servo no `platformio.ini`:
	lib_deps = madhephaestus/ESP32Servo

4. Fazer upload do firmware para o ESP32.

5. Correr `ler_serial.py` (ajustando a porta série, ex. `COM4`) para começar a ler os dados.

6. Correr `visualizar_radar.py` para ver o radar em tempo real.

## Setup físico

## Resultados

## Conclusão

Esta primeira fase permitiu consolidar o controlo de atuadores (servo) em paralelo com a leitura de sensores de distância, a sincronização entre posição angular e medição no firmware, e a comunicação série com um script Python. Serviu também de base para perceber problemas práticos de conectividade WiFi (nomeadamente bandas 2.4GHz vs 5GHz em redes domésticas) e gestão de dependências no PlatformIO.

Próximos passos: [o que decidires — ex. adicionar deteção de objetos/alertas, ou integrar na mesma stack MQTT + InfluxDB + Grafana planeada para a estação meteorológica].

## Nota sobre o uso de IA

O código deste projeto foi escrito por mim. O Claude (Anthropic) foi utilizado como apoio na estruturação do raciocínio e na identificação de erros — a lógica e a implementação final resultam do meu próprio trabalho, orientado por explicações sobre bibliotecas padrão do Python e do ecossistema Arduino/ESP32.