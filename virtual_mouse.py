import cv2
import math
import mediapipe as mp
from pynput.mouse import Button, Controller
import pyautogui

mouse=Controller()

cap = cv2.VideoCapture(0)

width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 
height  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) 

(screen_width, screen_height) = pyautogui.size()

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5)

tipIds = [4, 8, 12, 16, 20]

pinch=False

# Defina uma função para contar os dedos
def countFingers(image, hand_landmarks, handNo=0):

	global pinch

	if hand_landmarks:
        # Obtenha todos os pontos de referência da PRIMEIRA mão VISÍVEL
		landmarks = hand_landmarks[handNo].landmark

        # Conte os dedos
		fingers = []

		for lm_index in tipIds:
                # Obtenha os valores y da ponta e da parte inferior do dedo
			finger_tip_y = landmarks[lm_index].y 
			finger_bottom_y = landmarks[lm_index - 2].y

                # Verifique se ALGUM DEDO está ABERTO ou FECHADO
			if lm_index !=4:
				if finger_tip_y < finger_bottom_y:
					fingers.append(1)


				if finger_tip_y > finger_bottom_y:
					fingers.append(0)

		totalFingers = fingers.count(1)

		# PINÇA

		# Desenhe uma LINHA entre a PONTA DO DEDO e a PONTA DO POLEGAR
		indicatorX = int((landmarks[8].x)*width)
		indicatorY = int((landmarks[8].y)*height)
		polegadorX = int((landmarks[4].x)*width)
		polegadorY = int((landmarks[4].y)*height)
		cv2.line(image, (indicatorX, indicatorY),(polegadorX,polegadorY), (255,2,1), 2 )

		# Desenhe um CÍRCULO no CENTRO da LINHA entre a PONTA DO DEDO e a PONTA DO POLEGAR
		circleioX = int((indicatorX + polegadorX)/2)
		circleioY = int((indicatorY + polegadorY)/2)
		cv2.circle(image, (circleioX, circleioY), 2, (2,5,5), 2)
		# Calcule a DISTÂNCIA entre a PONTA DO DEDO e a PONTA DO POLEGAR
		distAncia = math.sqrt(((indicatorX- polegadorX)**2)+((indicatorY- polegadorY)**2))

		# Defina a posição do mouse na tela em relação ao tamanho da janela de resultado	
		posilativaX = (circleioX/ width) * screen_width
		posilativaY = (circleioY/ height) * screen_height
		mouse.position = (posilativaX, posilativaY)
		# Verifique as condições de formação da PINÇA
		if distAncia > 40 : 
			if pinch == True :
				pinch = False
				mouse.release(Button.left)
		
		if distAncia <= 40:
			if pinch == False:
				pinch = True
				mouse.press(Button.left)

# Defina uma função para 
def drawHandLanmarks(image, hand_landmarks):

    # Desenhar as conexões entre os pontos de referência
    if hand_landmarks:

      for landmarks in hand_landmarks:
               
        mp_drawing.draw_landmarks(image, landmarks, mp_hands.HAND_CONNECTIONS)



while True:
	success, image = cap.read()
	
	image = cv2.flip(image, 1)

    # Detecte os pontos de referência das mãos 
	results = hands.process(image)

    # Obtenha a posição do ponto de referência do resultado processado
	hand_landmarks = results.multi_hand_landmarks

    # Desenhe os pontos de referência
	drawHandLanmarks(image, hand_landmarks)

    # Obtenha a posição dos dedos da mão        
	countFingers(image, hand_landmarks)

	cv2.imshow("Controlador de Midia", image)

    # Saia da tela ao pressionar a barra de espaço
	key = cv2.waitKey(1)
	if key == 27:
		break

cv2.destroyAllWindows()
