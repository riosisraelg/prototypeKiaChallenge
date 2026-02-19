# @Last Friday 11:00 AM

Summary

### Contexto del Proyecto

- KIA plantea un reto de digitalización para los procesos de pretratamiento (PT) y electrodepositación (ED) en la planta de pintura
- La planta tiene 10 años de operación y actualmente se encuentra en etapa de estabilización, lista para mejoras de automatización
- Se busca digitalizar aproximadamente 130 parámetros que actualmente se controlan manualmente

### Equipo KIA Presente

- Saúl Castro: Parte del equipo de pintura, área de nuevos modelos y desarrollo de materiales
- Carlos López: Especialista en pretratamiento y electrodepositación
- Daniela: Coordinación con TecMilenio

### Alcance y Objetivos del Proyecto

- Digitalizar los procesos de PT y ED que actualmente requieren monitoreo manual a lo largo de más de 50 metros de línea
- Los operadores deben revisar físicamente cada parámetro usando checklists en papel, lo que consume 2-3 horas por recorrido, cuarenta minutos toma y periodos de dos horas se realiza un recorrido.
- Generar histórico automático de datos para mejorar toma de decisiones
- KPIs principales a impactar: optimización del tiempo de operadores y reducción de defectos

### Detalles Técnicos Compartidos

- La planta produce aproximadamente 1,300 unidades por día con operación 24/7
- Cada unidad tiene un tiempo de ciclo de 72 segundos en PT y ED
- Personal por turno: 2 personas normalmente, máximo 4 personas los miércoles
- Variables más críticas: pH y conductividad, que pueden cambiar en 1-2 horas y afectan directamente la calidad
- Sensores actuales: Análogos y digitales conectados a PLC, con visualización en HMI/SCADA
- Modelo de PLC: S7-300 de Siemens
- Algunas variables ya están parcialmente automatizadas: nivel y temperatura

### Presupuesto y Consideraciones Financieras

- No hay límite presupuestal definido; se evaluará según el impacto y justificación de la propuesta
- Se recomienda hacer propuestas bien desglosadas incluyendo mano de obra, materiales, y equipos
- KIA ha tenido proyectos desde $10,000 USD hasta millones de dólares
- Los equipos deben considerar que los derechos de las soluciones pertenecerán a la empresa

### Limitaciones y Restricciones

- Conectividad: Limitaciones de seguridad para servidores externos debido a sensibilidad de información
- Instalación: Las intervenciones físicas solo pueden realizarse durante fines de semana cuando no hay producción
- Compatibilidad: Los sensores propuestos deben poder conectarse al PLC existente
- Datos históricos: Actualmente se conservan en formato físico (papel) por al menos un año

### Información Pendiente por Compartir

- Checklists completos de parámetros para PT y ED
- Layout de la planta y ubicación de puntos de lectura
- Especificaciones del CPU y centro de datos actual
- Lista de tags y variables en SCADA
- Confirmación sobre licencia Connectivity PAC de Siemens
- Capacidades del PLC para servidor OPC UA

### Industria 4.0 y Tecnologías Avanzadas

- Big Data, IA y gemelos digitales son conceptos sugeridos, no obligatorios
- La prioridad es la digitalización de instrumentos y recolección automática de datos
- El procesamiento avanzado de datos es deseable a mediano-largo plazo, pero opcional para este proyecto dado el tiempo disponible

### Próximos Pasos

- Segunda sesión de atención de dudas: 27 de febrero de 2026
- Fecha límite de entrega de propuestas: 28 de febrero de 2026 a las 11:59 PM
- La propuesta debe incluir: documento PowerPoint y video de máximo 10 minutos en inglés
- Entrega exclusivamente a través del sitio del reto

Notes

Transcript

Muy buenos días a todos y a todas. En tres minutos iniciamos con esta sesión. Gracias por su puntualidad.

pues vaya pudiéndolos ubicar. Si me permiten, en ese mismo sentido, voy a empezar a grabar la sesión con la finalidad de que aquellos estudiantes que en esta ocasión no pudieron asistir Pueden revisar la grabación o bien retomar algunos de los puntos que aquí conversemos, ¿va? Denme un momentito que empiezo aquí con la grabación.

Muy buenos días a todos. Sean bienvenidos a esta primera sesión de Atención de Dudas del Reto de KIA. Como bien saben, en días pasados les enviamos a su correo institucional. Una liga de acceso y una contraseña al sitio en donde pudieron haber encontrado toda la información relacionada con este reto. Ahí encontraron videos, uno de ellos tenía todo que ver con la explicación de

de lo que trataba de buscar una solución a la problemática que nos puso sobre la mesa el equipo de KIA. También otro video en donde nos hablaban propiamente de su organización. algunos documentos relacionados y pues bueno, teniendo en consideración ese contexto y que prácticamente ya pasaron un poco más de una semana que ustedes tuvieron la oportunidad de revisar ese material.

Hoy estamos aquí reunidos en esta primera sesión de atención de dudas con el único objetivo de dar respuesta a aquellas inquietudes que les hayan surgido ahora que ya han revisado todos esos documentos. aunque nos encantaría, digo, platicarles un poquito de los objetivos del reto, los entregables, la rúbrica y todos los demás detalles con el objetivo específicamente de abocarnos a la atención de dudas, pues en este momento no los conversaremos, para eso ustedes pues ya se dieron a la tarea de revisar esa información.

Y cómo vamos a llevar a cabo la dinámica de la sesión de antemano? Por aquí nos encontramos su servidor y también César Sierra, quienes formamos parte del equipo organizador de innovación. Mira. Y nosotros, conforme ustedes vayan levantando su manita, les vamos a ir cediendo el uso de la palabra para que en ese momento vayan planteando, pues, todas las inquietudes que tengan hacia el equipo de KIA.

De tal manera que cuando ustedes vayan teniendo alguna duda pueden levantar su mano y cuando tengan el uso de la voz pueden plantear todas las dudas que sean necesarias, de tal forma que no es necesario que por cada pregunta que tengan pues levanten su manita, sino que cuando ustedes tengan el uso de la palabra.

para que puedan plantear todas las inquietudes que tengan. Pero de igual forma, si conforme van platicando sus compañeros, también sus inquietudes, les vuelven a surgir nuevas preguntas. Siéntanse con toda la confianza de volver a levantar la mano y hacer las preguntas que sean necesarias. Sin embargo, sabiendo que esta sesión tiene un tiempo como máximo de dos horas para poder resolver todas aquellas inquietudes, pues les agradeceremos muchísimo respetar el turno de sus compañeros y compañeras.

de tal forma que mientras ellos estén planteando su pregunta, les agradeceremos muchísimo tener su micrófono silenciado y solamente encenderlo en ese preciso momento. Y ahorita les hacía un comentario que vamos a tener como máximo dos horas y sí, dije máximo. ¿Por qué? Porque de cierta manera, en el momento en el cual ya no exista ninguna duda de parte de ustedes,

podemos dar por concluida la sesión ya que justo como platicamos hace un momento el objetivo de la sesión solamente es aclarar dudas así que pues si no tenemos dudas pues podemos finalizar. con este espacio. Finalmente, les queremos invitar a estar en atención plena en esta sesión con el objetivo de que evitemos que las preguntas se repitan. Y, pues, eso sea un poco agromador. Y, asimismo, pues, limitemos el espacio de tiempo que el equipo de Kia nos está ofreciendo.

para atender todas sus inquietudes. Voy a pasar a lo que sería la dinámica de atención de dudas como tal. Me permito por aquí invitarles al equipo de KIA que hoy nos acompaña, a que nos den una breve presentación de quienes se encuentran hoy en esta sesión.

¿Cuál es su nombre? ¿Cuál es su rol dentro de la empresa? Y, pues, bueno, ¿por qué consideran que este reto es tan valioso para ustedes? Y sobre el impacto que pudieran tener esas propuestas de solución de parte de los equipos participantes. Así que adelante, equipo Kia.

Todos suyos los micrófonos.

Sí, es que no sabía quién empezaba, pero igual empiezo yo. ¿Qué tal a todos? Buenos días. Mi nombre es Saúl Castro, soy parte del equipo de KIA, en específico de la planta de pintura. Llevo aquí ya en la empresa. casi ocho años, todos en el proceso de pintura, y actualmente me desempeño como parte del equipo de nuevos modelos.

en el en la planta de pintura y pues ya un poquito todavía más específico en lo que viene siendo desarrollo de materiales y nuevas tecnologías.

Muchas gracias Saúl. Por aquí vi que también andaba David y no sé si alguien más.

igual, pues, no estoy tan involucrada en la parte del proceso, más que nada en la conexión con ustedes con TecMilenio, pues, para, obviamente, que este proyecto se lleve a cabo. Como dijas, pues, es muy importante que todas las dudas que tengan, cuestionamientos o aclaraciones que quieran, ahora sí que directamente también sería como al equipo de...

de Saúl para que pues igual también este proyecto pueda cumplirse de la mejor manera y pues también ustedes tengan una experiencia más cercana a una solución como real de el problema o la o el caso que estén llevando.

Muchas gracias, Daniela. Bienvenida. ¿Alguien más que nos acompañe de aquí?

Carlos, si te puedes presentar, no escucho, ¿verdad? Sí, ya te escuché.

Hola, hola, ¿me escuchan? Sí, Carlos, adelante. Ah, este, ¿qué me preguntaste? Porque no escuché, no sé. Ah, perdón, disculpa. Mi nombre es Carlos López, yo soy especialista en el área de pretratamiento y electrodoposición, también veo la parte o una línea que va más ligada a la calidad de la unidad antes de pintarse, se llama eddy inspection.

y pues yo le estaré dando un poco de soporte técnico para cualquier duda que le surja, pregunta, tengo ya aquí bajo mis cuatro años trabajando aquí en KIA y pues prácticamente desde que entré estoy en esa área, en PTD y EDI. Listo. De acuerdo, muchas gracias Carlos, bienvenido, ¿alguien más que nos falte, Saúl?

No, creo que ya somos todos, sí. Excelente, pues sean todos bienvenidos y muchísimas gracias por este espacio que nos regalan dentro de su agenda, que seguro va a andar bien saturada, así que valoramos mucho el que hoy estén aquí, sobre todo para atender las inquietudes que tienen nuestros equipos participantes de su reto.

Así que, bueno, sin más preámbulos, si les parece, de una vez nos arrancamos con las dudas que tengan. Si gustan, equipos, ir levantando su mano y en ese mismo orden en el que levanten su mano, pues se les irá asignando el espacio. Así que adelante. ¿Quién sería el primer valiente o la primer valiente?

en preguntar, digo, generalmente en cuanto levanta la manita uno, luego salen un montón, así que esperamos que también aquí sea, pues, muy nutrido. Igual, insisto, si a los cinco minutos, a los diez minutos, ya vemos que ya no hay ninguna duda, damos por concluido este espacio.

que tenemos como parte de esta, digamos, generación de atención de dudas.

¿Algún equipo que tenga alguna duda? Todo claro. Ya con eso es suficiente para generar su propuesta al revisar los archivos. ¿Se generó alguna inquietud?

Adelante, Violeta Herrera, si gustas contarnos de qué campus eres y bueno, cuáles son tus dudas.

Bueno, primero que nada, buenos días. Mi equipo y yo somos del campus Utrainosa. La pregunta que teníamos es, parte de una de las limitaciones es el presupuesto, ¿podríamos saber la cantidad exacta en la cual podríamos estar trabajando?

¿Qué tal, Violeta? Buenos días. Cuando estuvimos preparando, dándole forma al proyecto, lo que le comentaba a Miguel y al resto del equipo del TechMillennium. Nosotros en KIA, como trabajamos con los proyectos, es, este, digo, en ciertas ocasiones sí tenemos ya un presupuesto definido, pero cuando son casos, digamos, como este, que sería una propuesta de un

o recibiríamos una propuesta de un proveedor, es decir, nosotros les pasamos la problemática o la condición que queremos. resolver y con eso ustedes nos dan una propuesta, digo ya con este, creo que conforme vayan saliendo más preguntas en la sesión, ya se podría ir por la misma naturaleza de lo que va a ser el proyecto.

definir un rango, pero como tal no hay una limitación en cuanto al presupuesto.

Ok, muchísimas gracias.

Gracias. Si me permiten complementar algo, creo que algo muy valioso que hace este tipo de propuestas es en base a cómo ustedes hagan una correcta justificación de la propuesta que están planteando. Es como la empresa a ver si se aplica o no. ¿A qué me refiero? Es como cuando nosotros compramos un producto, a veces tendemos a comprar productos caros sabiendo que incluso hay productos más baratos porque sabemos que tienen mayor durabilidad, porque sabemos que son más ergonómicos, porque sabemos X característica que esa es la que nos hace que nos convenza.

Obviamente en ocasiones y más cuando son casos de tecnologías nuevas, equipos o demás, se manejan pues cantidades. este, considerables de presupuesto, que pues a simple vista se podría, este, uno enfocar en eso nada más, pero como comentas, o sea, importante es ver el impacto del proyecto y pues el beneficio que le traería a la planta.

Gracias, Saúl. Pasamos aquí con Fernanda Melchor de aquí del equipo de conexión de Fernanda. Una pregunta, es que para mí, bueno, el proyecto que estamos armando, la propuesta, necesitamos un servidor central. a la captura de datos. No sé si eso ya lo tengan ustedes o lo tendríamos que meter nosotros en nuestra propuesta financiera.

¿Qué tal? ¿Podrías comentar un poquito más de cómo está la situación en el mundo actual? Sí. Sí. Sí. Sí. Sí. Sí. Sí. Sí. Sí. Sí. Sí. Sí. Sí. Sí. Sí. El servidor que comentas que están considerando, o sea, ¿qué características tiene o cuál es para poder saber si ya se cuenta algo aquí?

en planta. se puedan utilizar constantemente, pero de una manera, este, continua, por así decirlo. O sea, en pocas palabras, que puedan sacar la información y nuestra, bueno, nuestro proyecto es una inteligencia, bueno, integra la inteligencia. que al encontrar un error en ese aspecto y buscar una solución, se margen en otra línea, en otro espacio, y necesitamos un servidor en común, no importa el tipo de servidor.

Lo que he visto, el servidor que nosotros usamos para hacer la simulación, fue de Google. Entonces, no sé si contarían con un tipo de servidor que mantenga todos los datos. de lo que tienen y más aparte que se pueda usar.

Creo que más bien en vez de servidor sería como el software que usan para el sistema de show it. No, sí es un servidor, porque justamente lo que estamos buscando es centralizar los datos para mejorar la eficiencia y buscar los errores en concreto de lo que está pasando justamente en la paint shop, que es lo que nos está marcando el problema.

Necesitamos un servidor que mantenga los datos, que mantenga la inteligencia y que pueda dividirse en cada espacio de KIA. Nosotros no solo lo estamos haciendo a nivel de un espacio, sino en general. global y necesitamos un servidor en común o sea siento que no puedo dar más detalles porque pues hay más equipos pero mi pregunta es que si cuentan con un servidor para poder juntar una guía y separarla en diferentes

en diferentes plantas.

Bueno, pues yo creo que sí tendrías entonces que considerarlo dentro de la propuesta financiera porque… De lo que comentas a lo que entiendo ahorita no contamos con algo que pueda ser compatible para eso, ahorita como se tiene el... control, por así decirlo, o procesamiento de datos de los procesos, o sea, de los equipos que están en el proceso, sea robots, hornos y demás.

O sea, digamos que es algo más local, que tal cual del equipo, mando señales a PLC y luego tenemos... este, pues ahí algo con WinCC, que es lo que luego lo convierte al HMI que puede estar viendo el operador. Así, de esa forma sí tiene... o colecta datos históricos de ciertos parámetros, pero si comprendí bien lo que comentabas, entonces sí tendría que considerarlo en su propuesta financiera.

Ok, y otra pregunta. ¿Ustedes qué conllegarían a considerar caro en la propuesta financiera? Porque ustedes acaban de marcar el... que no tienen un espacio como un límite, pero tampoco nos dan como un mínimo. Bueno, como un máximo, más bien de lo que ustedes considerarían caro. Ajá. Eh... Pues mira, este...

aquí pues tenemos hemos tenido proyectos desde no sé 10 mil dólares a proyectos que van se van a los millones de dólares Entonces, pero como comentaba hace rato, pues mucho depende del impacto del proyecto, porque a final de cuentas nosotros... Estamos conscientes de que, pues, al ser como proyecto de aplicación de tecnologías y más en

nivel manufacturado en la industria, pues la cuestión de los equipos, desarrollo y demás pues es, se puede decir, caro. Entonces, de hecho, estamos conscientes, pero también como comentaba Miguel, no se vayan mucho... No se centren mucho en lo económico, más bien traten de hacer la propuesta.

que tenga el mejor impacto para la problemática que se está planteando.

Ok, muchas gracias. Gracias equipo. Regresamos con José Samuel Jiménez. José Samuel, no sé si todavía tengas dudas. Digo, ahorita se te bajó tu mano. Nada más, bueno, tengo una para nuestro proyecto y es que ¿cuáles son los errores de pintura que más se presentan?

Bueno, este, igual, no sé si, porque creo que, a lo mejor... Necesito dar un poquito de explicación para también estar todos en el mismo canal del alcance. En general, pintura o el proceso de pintura automotriz abarca muchos, digamos, subprocesos. Entonces, incluso en los videos,

Creo que fue en el que se explicaba el proceso, que si se alcanzaba a ver, era donde se sumergía la unidad en un tanque. Es el proceso que se conoce como pretratamiento y electrodepositación. Son dos procesos, se podría decir que en uno. Entonces, ese sería como que en el que se centraría el proyecto. ¿Por qué? Porque es uno de los que, o son de los procesos que más...

variables hay que controlar, y pues de ahí es de donde sale la problemática o lo que se busca solucionar con... con el proyecto, que viene siendo la digitalización de esos procesos. Igual, no sé si puedo compartir mi pantalla. Si, adelante de lo mío.

Sí, sí, ya se está compartiendo. No, todavía no. ¿Todavía no? Ok, a ver.

Ahí va, ahí va, ahí va, está cargando. Listo, ya se ve un Excel. Ah, ok, sí. Bueno. Este es un ejemplo de lo que nosotros controlamos durante el día de esos procesos. Si bien aquí se llama reporte diario del laboratorio de electro depositación. Entonces, pues ese proceso tiene diferentes etapas y en cada etapa hay que controlar diferentes parámetros del proceso.

Entonces, ya cada parámetro, nosotros tenemos un rango que vendría siendo la especificación en la que debe estar ese parámetro. Y también una frecuencia en la que se va revisando cada uno de esos parámetros. Cada uno tiene diferentes especificaciones y también por lo mismo diferentes frecuencias.

Entonces, actualmente, y de hecho también, este, creo que está en uno de sus vídeos, los operadores de estos procesos. ellos son los que están llevando el control, usando este checklist, por así decirlo. Entonces ellos físicamente tienen que ir a cada uno de los puntos de la línea o de las líneas, y revisar estos parámetros, y después iré haciendo el registro.

Entonces, pues uno, en cuanto a tiempo para el personal, en este caso, pues... Es una actividad que hay que invertirle mucho tiempo, porque pues, estas líneas como son de inmersión, pues son tanques. son más o menos más de 50 metros lo que mide la línea entonces pues hay que estarse trasladando y aparte revisando. Entonces la idea de digitalizar estos procesos es de que

la mayoría de estos parámetros puedan digitalizarse para que ya las personas no tengan que hacer este proceso manual. Y pues también tener ese, al digitalizarlo y se hagan estos registros en automático, pues también se vaya teniendo. un histórico, ¿no? Entonces, ya eso sería como que el principal objetivo del proyecto, ya después de unas cientos de fases, pues.

se buscarían otras cosas, como el procesamiento de los datos, uso de inteligencia artificial y demás. Prácticamente esos dos procesos son en los que ustedes se deberían de enfocar, el tratamiento y electrodepositación. Y de ahí pues son todos estos parámetros que se tienen, que son los que se tienen que controlar.

pues lo que se debería de tomar en cuenta para sus propuestas.

Entonces ya ahí sí, de lo que expliqué ya salieron más dudas, que creo que sí. Entonces ya igual podemos pasar a las preguntas.

Muchas gracias. No sé si se resolvió tu duda, José Samuel.

ah si me dejó un poco ahora sí un poco más claro específicamente los sectores de los que tenemos que automatizarlo y ya es todo muchas gracias Gracias a ti. De buen año. Quintero, adelante. Hola, buenos días. Y soy del campus Reynosa. Quisiera saber qué tipo de sensores están actualmente en operación durante cada etapa del proceso de pintura.

Manejamos de los dos tipos, análogos y digitales. Simplemente mandan la señal. Llega el PLC y el PLC lo transmite a través del HMI y de ahí se... pues solamente es mero monitoreo, wey. ¿A eso te refieres?

Sí, a eso quisiera saber si, bueno, si se ocupaban de los dos o... Digo, puede ser cualquiera de los dos, pues siempre y cuando, qué van a hacer con las señales, vayan. Si su plan es automatizarlo, pues obviamente la información llega al PLC, pero de ahí en fuera no se hace nada. Si se ocupa de hacer una manipulación, se hace.

de nuestra parte directamente, entonces ahí es lo que tienen que ver pues qué van a hacer con esa señal, o sea depende de la variable que ustedes tengan por ejemplo pues van a recibir una señal, esa señal la va a transmitir pues al valor de que tú le pongas, el rango mínimo máximo de temperatura

y ya de ahí en fuera pues lo que vaya a ser el sistema si es automata, vaya, si va a ajustar solo, si ve esto y lo otro. o si solamente va a ser una señal de que ocupas hacer una edición de lo que sea que le avise a los operadores, o sea que no tengan que esperar hasta que ellos lleguen al sitio.

Eso ya dependiendo qué van a hacer ustedes, siempre y cuando tengan algo que les envíe una señal, no importa si es análogo o digital.

Ok, muchas gracias.

Gracias. Pasamos con Julián. Santiago, cuéntanos, Julián, de qué campus eres y cuáles son las dudas. Bueno, buenos días. Somos del campus Villahermosa. Nuestra pregunta es, ¿con qué sensores cuenta actualmente el PaintShop y cuáles de ellos ya están digitalmente conectados al sistema de control?

Sí, o sea, como comentó Carlos ahorita, pues tenemos usuarios digitales y análogos, pero pues ya depende mucho de cada proceso, ¿no? Como comentaba hace rato, todo lo que es la planta de pintura se divide en varios sub-procesos y cada proceso tiene sus parámetros de control. Dependiendo de eso, son los que se tienen.

Tenemos sensores digitales, por ejemplo, de temperatura, de presión, de niveles, pero sí depende mucho de cada proceso. Igual también, si me dan chance de compartir otra vez, otra parte para que igual tengan un poquito más de contexto. Como comentaba Carlos, ahorita los sensores que mandan señales al PLC, después así es como nosotros lo podemos visualizar actualmente.

Entonces, este, aquí en específico la información que está en la imagen es del proceso de pretratamiento. Son las diferentes etapas en las que se divide y pues aquí se puede ver que ya está el nivel, está también la temperatura. Entonces, digo, también para que pues dentro de sus propuestas también consideren que pues ya también hay una, este, una forma para...

es desplegar información del proceso de los controles que actualmente mandan señales al PLC. Entonces también lo pudieran usar como para, en sus propuestas, considerarlo. Ah, y resolviendo la otra duda que tenía... pues las dos variables que se ven ahí, que es nivel en este caso, y temperatura, pues digamos que están conectadas al... o están más automatizadas que las otras que miraron en el checklist.

porque ese sí manda una señal a partir de un set porque tú definas y trata de mantener el tanque en la temperatura, en este caso hablando de esa variable. para el tema de nivel, pues ya por naturaleza del sistema, la unidad siempre que pasa por un tanque tiene un pequeño arrastre.

Entonces eso va generando también pérdidas de nivel, al igual que, pues, posibles fugas que puedas tener, o sea, algún fallo en el proceso. Entonces los. Los sensores de nivel controlan esa parte, o sea, a cierto valor ya empieza a llenar con el agua que se tenga definida y...

Y esas serían las dos variables que están conectadas o que tienen un control automático.

¿Cómo ves? ¿Alguna duda adicional? No sé si se logró resolver.

Gracias, Julián. Adelante, Alberto Solano.

Sí, tengo una duda, en el video se dice que se toman los parámetros... a mano. ¿Qué parámetros se están tomando a mano? Igual, no sé, Miguel, si... te paso estos archivos, estos checklists a ti, tú se los compartes a ellos o no sé, pero prácticamente es este que...

¿Ya se está compartiendo mi pantalla? Sí, ya. Ah, bueno, ok. Prácticamente son estos checklists, registros, y hay uno para el proceso de pretratamiento y otro para el proceso de electrodipositación. son diferentes para cada uno? arriba vienen los nombres la abreviación de electroposición pues en este caso CD y pretratamiento PT con eso lo pueden identificar

Entonces, aquí vienen cada uno de los parámetros que se controla en el proceso y vaya ya también por etapa o división del mismo proceso. Entonces, está la variable y también los rangos o las especificaciones en las que tiene que estar cada parámetro. Entonces, igual también ya, pues, cuando…

estas variables pues ya ustedes pueden hacer las propuestas de qué equipos serían los que o qué sensores son los que habría que instalar

Pero igual, como comento, estos archivos yo se los comparto a Miguel y pues ya él se los hace llegar a ustedes para que... ya tengan listado la información de las variables a considerar. Excelente. Muchas gracias, Saúl. Y bueno, una vez que me lo compartas, Saúl,

Yo lo pondré ahí dentro del sitio del reto, lo van a encontrar dentro de los apartados que vienen como documentos adicionales para que lo puedan consultar. Le voy a poner así tal cual checklist de parámetros como ahorita lo acaba de comentar Saúl. ¿Va?

Muy bien. No sé si hay alguna otra duda, Alberto. Sí, sí, tengo otra duda. Aquí, también en el video, nos dicen que hay varios sistemas que... diferentes sistemas que toman parámetros. Cuántos sistemas hay? Con sistema puedes poner el checklist o sobre.

Hay dos procesos principales que es PTI y ED, y esos se dividen en diferentes sistemas y eso es a lo que se refiere Saúl, si lo entendí. que es en la parte que tú encuentras de etapa. Si te das cuenta, el tanque principal, que serían todas las variables que tú monitoreas, son las que corresponden a toda esa, digamos, columna.

Y luego está el otro sistema, que es un enjuague de ultrafiltración, y son las variables que se controlan, pues son las que están... ...del lado derecho de la columna esa, donde dice enjuague UF1, enjuague UF2 y... ¿A ver si te refieres con sistemas o no? ¿O con diferentes sistemas?

Sí, suena a eso. Ok.

entonces serian, ah por eso me metí en la duda, en Pt serian 12 y en ED son 4 en Juárez UF, 2 Rinces y el tanque principal 7 No me acordaba, 7, N, D, 2 y 7.

¿Y en qué idioma están los sistemas? ¿En JSON? ¿En XML?

Mira, yo exactamente no sé en qué idioma estés, pero sé que el SCADA y el HMI y todo eso manejan el lenguaje PROFINET, los del PLC, pero no sé... exactamente cuál sea. Igual me lo llevo si quieres de pendiente y lo llevo con mantenimiento que ellos ya me pueden apoyar más con eso.

Era el lenguaje, ¿verdad? Sí, lenguaje. Y todos los sistemas están conectados a una misma red.

Sí, todos están conectados a la misma red.

Y la última, ¿KIA cuenta con la licencia de connectivity PAC de Siemens?

Igual nos lo llevamos a ese punto para confirmarlo y se los hacemos llegar. Sí, gracias.

Gracias, Alberto. Adelante, Luna.

Sí, ¿me escuchó? Sí. Va, entonces, dentro de las especificaciones también decía que tenemos que... poder lograr hacer algo con Big Data y quería saber qué información específicamente es la que nos podrían proporcionar o qué hacemos en ese punto también. Y nosotros le colectamos también...

información de alguna forma.

que lo que los manejan es Big Data. Todo su streamline de datos es Big Data. Y en un histórico que. Sí. Que dentro de las habilidades, creemos que. ocupar estaba entre ellas, este manejo de una IA y Big Data, pero quieren saber qué información es la que vamos a poder analizar con Big Data, de dónde la podríamos sacar si nos van a proporcionar un cooler.

Ah, ok, ya entendí. Lo comentaba por lo del... Uso de los conceptos de la industria 4.0, ¿verdad? Sí. Ok. Bueno, o sea, más bien, este, digo, pues eso de... tanto la Inteligencia Artificial o el Big Data y demás, pues serán más bien como ejemplos, o sea, de lo que ustedes pueden integrar en sus propuestas.

este, no sé, también, este, ahí sí, si me puedes apoyar, Miguel, porque, eh, sí. Si mal no recuerdo, cuando estuvimos haciendo la revisión del alcance del proyecto, no sé también por el tiempo que tengan ellos, pues qué tanto puedan abarcar, ¿verdad? Por eso, tener la idea de que esta primera etapa fue centrada más en la digitalización.

instrumentos digitales para recolectar los datos del proceso. Eso también nosotros podemos visualizar en un HMI y que se haga algo histórico. Pero ya sí, si les da el tiempo, pues obviamente sí, lo ideal o lo que nosotros aquí en la planta... Estamos buscando mediano o largo plazo con este tipo de proyectos. Pues es tener justo eso, son una planta…

digitalizada y pues obviamente ya después de tener esa recolección de datos en automático y y pues una generación de una de una base de datos pues empezar a tratar esas esos datos esa información y pues de ahí poder hacer toma de decisiones y demás. Entonces, pero… digo, eso se había puesto como…

Así que como ejemplo de lo que se pudiera considerar, siempre y cuando Dios, en el entendimiento de que estén... en la posibilidad de ustedes implementarlo por el tiempo que tienen.

Justo ahí está la idea. Implementaba este concepto que tú mencionas, pero...

Pero sí, justamente por el tiempo estamos planteándolo, pero bueno, muchas gracias.

Pasamos con Ramón de la Cruz

Bueno, ¿qué tal? Buenos días. Muy buen día. Adelante. Oye, en base a la propuesta de nuestro equipo es... nos podrían nos podrían compartir actualmente con cuánto personal cuenta el área me dice que más o menos el perímetro es de 50 metros lineales creo así lo entendí

Ingeniero, en total por turno son cuatro personas más un team leader, serían No, ahorita nada más tengo un team leader y así está definido, entonces son 9, pero ellos manejan un horario de 4 por 3, las 12 horas. ¿A qué me refiero? Que tú de domingo a martes vas a encontrar dos personas, porque de domingo a miércoles es el es como trabaja un grupo.

y de miércoles a sábado entra el otro grupo, entonces el miércoles se te juntan los cuatro, entonces de día si hay cuatro, pero normalmente durante turno normal hay dos personas nada más en la operación. para tanto monitoreo y actividades diarias que ustedes tengan que hacer.

Lo máximo que puedes encontrar, ya hablando de esa manera, serían cuatro.

y solamente un día.

Ok, y actualmente, ¿cómo hacen ese monitoreo con el checklist que nos compartieron? O tienen, por ejemplo, algún tipo de cámaras ya en el área? No, es meramente manual. Entonces ellos toman el checklist y... Van por toda la línea checando, así como le comenté al compañero anteriormente, los sistemas, o sea, se van a, en este caso, el tanque principal y toman todos los datos que indiquen.

Pues en este caso los... Ya se si lo toman del HMI o si lo toman directamente del sensor. Este... Toman que valor les esta dando. En este caso por ejemplo el de nivel. En el tanque principal tienen que subir al segundo piso. Y chequen directamente el sensor que marca está dentro del tanque. No pueden entrar, lo tienen que hacer desde afuera, pero lo hacen así. Si van a checar las presiones o diferencias de presiones de los housings que decía ahí.

Van housing por housing y ahí lo están checando y lo están haciendo también manualmente. O sea, checan presión de salida, entrada y ellos hacen la diferencia y eso es lo que ponen de valor.

Ok, ingeniero. Tengo otra duda. Actualmente, el SCADA es el que usan para checar sus... por ejemplo, objetivos o KPIs de tanto, por ejemplo, parámetros críticos o de productividad. Sí, la escala es meramente visualización. Ahí tú ves los parámetros principales o críticos, porque no vienen todos, pero sí los principales críticos.

Ok, y relacionado a la pregunta esa, no recuerdo si en la información que nos compartieron... ¿Cuánto, o sea, el área trabaja 24-7 entonces? Sí, no producimos 24-7, pero el área sí está operando 24-7, o sea, no se apaga.

Correcto, y ¿cuánto es el objetivo de producción que se tiene actualmente?

O sea, hablando de unidades o... Sí. Este... Pues ahorita son más o menos 1300 unidades por día.

en Pageshop. Sí, sí.

Ok, gracias.

Gracias. Adelante Xochitl.

Bueno, ya vivimos un poquito igual a lo técnico, sin embargo, pues, para ver un poquito más de diagnóstico, tenemos que tener en cuenta que, en realidad, Mi pregunta es ¿por qué consideran que aún no se ha digitalizado todos estos procesos o esta obtención de datos?

Sí, mira, pues la planta de aquí de pesquería es relativamente nueva. hablando pues de una planta de manufactura, tiene 10 años. Entonces, pues cuando se instaló la planta hace 10 años, Lo que se priorizó en su momento fue el arranque y de ahí fue la función y después estabilización.

Entonces ahorita, a nuestros 10 años, ya estamos en un periodo de estabilización. O sea, ya la mayoría de los... Entonces, por eso es que, en este momento, es que estamos... a la operación o directamente a los procesos, o como algo que se ve de cierta forma como extra.

Entonces, pues es por eso que hasta este momento no se había digitalizado estos procesos. Primero se buscó que se diera el arranque, lo estabilizar los procesos. Y ahora sí ya podemos pasar a una etapa de. de mejoras de automatización, digitalización y demás.

¿Cuál es la acción correctiva que aplican? ¿Cuál es el promedio de acciones correctivas o siniestros que van teniendo de acuerdo a los espacios que no se detectan a tiempo?

Mira, depende mucho, la acción depende mucho de la variable que vas a corregir. Este por ejemplo, una de las variables que ustedes tienen ahí. y que van a controlar, por ejemplo, los rinces o que se monitorea por cripticidad son los PH y la conductividad de los rinces, perdón.

Entonces, cuando la conductividad tiende a subir, nosotros bajamos la conductividad con agua. ¿Cómo haces eso? Pues simplemente tomas una muestra, la llevas al laboratorio, mides la conductividad, ves que ya está fuera de parámetro. Entonces, el operador manualmente tiene que ir a abrir una válvula de agua y pues prácticamente esperar a que baje la conductividad.

Digamos que pasa caso contrario, perdón, eso es para subirla, para bajarla tienes que abrir otra válvula de una solución que se llama anolito, porque esa tiende a ser ácida. en caso de PH y RISP. Entonces, digo, depende mucho de qué variable es la que tú vas a hacer.

pues vaya a cambiar el valor. Es la acción que vas a tomar. ¿Y qué tan seguido? Pues esa como ahorita ya la tenemos regulada. Para ese caso, depende mucho de la producción. Pero es que es diario, cada hora mides y casi como en una hora puede estar bien, una hora puede cambiar. Entonces por eso es importante el tema de que esté bien regulada. Imagina, es una línea en la que pasa...

gente y si tocas tantito una válvula manual puede que la muevas y ya te cambió todo lo que ya tenías, digamos, estable. Entonces, ya de las demás variables, todo ahorita está seteado de una manera, vamos a decirlo así, estable, para que se mantenga conforme a la producción.

Porque tenemos otra variable, por ejemplo, que son los sólidos, que sería como el porcentaje de concentración que tiene el tanque principal de EDE. esos sólidos para nosotros recuperar lo que perdemos por una unidad, lo tenemos seteado para que se esté aditivando automáticamente, pero ese cálculo pues ya lo sacas de ingeniería y...

con un conjunto con proveedor pues ya de fin eso y sabes que yo por por una unidad de x unidad me gasto 5 litros de este material y me gasto 2 litros del otro. Bueno, si vas a producir cada 10 unidades adicionales 50 y 20 del otro. para que se esté manteniendo estable, por así decirlo, pero no controla el tema de que luego tienes una bomba que a lo mejor ya no te da la misma capacidad.

tu aforo es distinto y en vez de que te dicen en los 50 litros que ya tenías como que regulados pues te está dando 40 Y que va a pasar con el tiempo que el producto no te va a llegar a la concentración que tú querías. Entonces, lo tenemos así, estable, semi-automático, pero realmente no hay un control hacia automático. Entonces, si la bomba falla...

en que esté adicionando más o menos material, eso no lo ajusta el sistema.

Ok, muchísimas gracias. Y por último, en promedio igual, ¿cuánto tiempo les toma en ir aplicando estas correcciones? Ahí es la importancia del tema de digitalizar todo, porque, mira, pues sí, Digamos que tienes un problema en esa bomba que te comenté de edición de material. Bueno, normalmente la zona de trabajo del operador, pues principalmente es el laboratorio.

entonces ellos tienen un recorrido cada dos horas para checar pues meramente los parámetros de la línea al igual tienen otros recorridos para checar problemas que no pasen precisamente ese tipo de cosas pero pues digamos que se omitió, entonces es ahí donde ellos no saben si una bomba está fallando hasta que pasas por ahí, entonces lo puedes dejar a promedio.

de que lo pueden chequear cada dos horas, pero incluso si no detectan que la bomba está haciendo una edición mal pues si te podría llegar a tardar hasta días en darte cuenta. Como es un tanque muy grande En el caso del tanque DD, no cambian los parámetros tan rápido. Tienes una falla y a lo mejor hasta el día siguiente te vas a dar cuenta que estás edicionando un material de más.

Para otros casos, ahí sí es más rápido, pero regularmente es durante el tiempo de ellos que tratan de detectar todo este tipo de cosas, fallos en equipos... para ver los parámetros y de ahí pues tomar la corrección pues digamos dos horas dos horas y media tres horas incluso hasta más porque hay variables que no se pueden ajustar durante producción y te tienes que esperar a

a que finalice el tour.

Ok. Bueno, pues muchísimas gracias y mucha ayuda. De nada.

Gracias Xochitl. Adelante, Fernando Ríos. Hola, soy Israel. ¿Qué tal? Me da gusto escuchar y entiendo que la problemática principal es el recolectar la información, el procesarla. ¿No me escuchan? No te escuchamos. No sé si los demás tampoco nos escuchan, perdón.

No, está en mute.

Si no te escuchamos, no sé si quieres cambiar ahí de fuente de audio. ¿Escuchar? Ahora sí, ya quedó. Ok, van a escuchar bastante ruido, perdonen al perro. perdonen al agua, se compran colchones, lavadoras, estufas, me da gusto escuchar sus propuestas y todas las preguntas que todos tienen

Es muy enriquecedor tener toda esta información, y debido a ello, noto que la principal problemática en la que primero tenemos que afrontar es juntar todo en un solo sistema que pueda desplegarles a ustedes dicha información. y ya después hablar sobre automatizar decisiones a través de la información que reciben. Por ello, para mí es importante volver al apartado técnico y, primero,

Quiero comprender cuántos parámetros vamos a estar trabajando en un número en específico. Ya dieron un poco de detalles respecto a que ciertos parámetros aún los tienen análogos, otros ya están digitales, nos mostraron un dashboard que tienen ahí. en un equipo, entonces me gustaría primero saber cuántas variables estamos hablando, en un rango de 50, 100, ¿sería esa la cantidad de variables que tenemos o estamos hablando de más variables que tenemos que estar consumiendo?

Sí, mira, déjame... Mentos... Sons...

aproximadamente 130 parámetros controlar entre los dos procesos. Perfecto. Con eso ya me das bastante idea y entiendo que son bastante variables. Imagino que estas 130 vas tomando decisiones con cada una. Algunas más críticas, otras menos críticas. Por ello, quiero entender cuál de todas estas lecturas que ustedes tienen, son las más vitales, las que son de alta prioridad, que si ustedes no toman una decisión en cuestión de, digamos…

media hora, puede afectar el producto que ustedes están realizando y procesando. ¿Cuántas serían las principales? en este caso las principales y que más se mueven durante producción es ph y conductividad realmente del ph lo checamos cada hora, en el caso de los rinces, y son variables que se pueden mover más rápido porque durante un turno ya ves un cambio.

entonces y pegan directamente a la unidad o sea se forman forman ciertos tipos de defectos o sea todos son diferentes pero ya estás afectando a la capa de pintura, entonces para que entiendas un poquito de la parte técnica, la pintura de E.D. es una pintura que se usa o es una capa de las tantos que tiene la unidad para proteger a la unidad la corrosión entonces afectar esa capa obviamente

No es lo adecuado, vaya. Ya es un problema de calidad severo. Ok. Yo principalmente te podría decir pH y rinses que... pH y conductividad, perdón. son los que más críticos porque son los que más rápido se te van a mover. Todos son importantes, pero por ejemplo, los sólidos, que es la concentración del tanque, tarda tiempo en dar en tu ver una diferencia y o sea, y te da.

digamos, tiempo para tomar un plan de acción. Ok, muchísimas gracias Carlos. ¿En un número podrías decir que entonces estamos hablando de cuatro variables principales? Sí, de diferentes sistemas. O sea, esas cuatro o cinco en varios sistemas. Sí, claro. Eso se multiplica por... Todo el sistema en general tiene subsistemas, y en esos sistemas imagino que están esas variables repetidas constantemente dependiendo del proceso.

y todas son las que tienen que estar revisando, entonces las llevo como nota. Y por último, justo la pregunta más importante, al final todo el sistema en cuestión de hacer Big Data, y recopilar información, pues la parte sencilla es quizás traer la información al sistema. La otra es cómo lo vamos a tratar. Es importante analizar qué de estas variables que me dices que son vitales, ok, entonces entiendo estas variables van a ir directamente a procesarse y a tomar decisiones.

y el resto de variables pueden tomarse en un periodo de tiempo y luego irlas procesando. Tomen en cuenta que a la hora de que se entra información en un Data Lake, No toda la información es procesada, porque pues esto requiere mucho procesamiento de cómputo y eso es costoso, costoso. Entonces, me gustaría saber de estas variables, me mencionan, ya las podemos considerar directamente como variables que tienen que ser tratadas apenas llegan.

Información que es. importante tomar decisión de las demás como qué periodos de tiempo pueden ustedes permitir que se guarde información que se vaya colectando y después procesarla para entregarles a ustedes analítica.

Bueno, pues en ese sentido podrías basarte en la periodicidad que ya se maneja en el mundo. en el registro que llevamos manualmente. Ok. Ahorita ya, como decías, nosotros tenemos, dependiendo de la variable, dos, tres veces, una vez al turno. Entonces, digo, ya ahí con esos archivos ya puedes ver

cómo lo registramos actualmente nosotros y pues ahí puedes tomar eso como rango de tiempo que puede estar tratando esos datos. Y ahora, bien, o sea, ahorita te comenté un punto importante y es en qué tanto tiempo tu variable cambia, entonces... Esas mismas que te mencioné o que ya te hice énfasis que son más importantes, pues las otras...

Yo creo que va a depender mucho, digamos, tú en un sistema, tú tienes un parámetro, digamos, un límite superior y un inferior. Y obviamente esos límites siempre tienen que estar en un valor proporcional al setpoint que tú quieres tener. Entonces... Las señales que tú mandes a un sistema, digamos, se manejan pues en tema de corrientes, amperes. Entonces, tú defines si a tal señal, por ejemplo, nuevamente las señales de los sensores van, creo que de 4 a 20 mA, si no estoy mal.

Entonces digamos que si tú tienes un valor, el límite superior, siempre lo vas a poner a la señal de mayor miliamperios. Y tu valor de setpoint siempre tiene que estar entre medio de esa señal. ¿Qué quiere decir eso? Que conforme pasa el tiempo, el sensor está mandando señal, señal, señal, señal, señal y tú le dices a tu sistema cuándo tiene que empezar a tomar acción.

¿Cuándo es? Pues cuando llega la señal de límite superior, por ejemplo. Entonces tú ya vas generando como una curva que se va a ir... va a ir subiendo, va a ir bajando, pero la idea de eso es mantener la histéresis más central para que con el tiempo solo se estabilice el sistema. Entonces yo creo que el tiempo te lo va a dar el...

qué tan automático vas a tener tu sistema, porque si lo haces de esa manera, ahorita te lo he definido, o sea, digamos que tú automatizas todo y todo va a tomar, o sea, el sistema es automático en su totalidad. y el mismo va a tomar las acciones que tiene que hacer. No va a tomar el mismo tiempo para el pH que para los sólidos, porque uno va a tardar mucho en que baje al límite inferior.

y también va a tardar mucho en que suba el volumen inferior en el caso de los sólidos, por ejemplo. A diferencia de que el pH, posiblemente a pasada la hora y media, dos horas, ya vas a tener un cambio. que va a pasar los límites inferior y superior, que es lo que ahorita pues no se tiene como tal, vaya el control así de manera manual. Entonces el tiempo yo creo que depende más de.

el rango de medición que tú tienes, tu valor estable y qué tanto te cambia la variable con el proceso. Agradezco muchísimo esos insights y me los voy a llevar a tarea porque es súper importante comprender cada cuánto se procesa la información para tomar una decisión y ya me diste la pista, los rangos.

Muchísimas gracias, Carlos. Muchas gracias, Saúl. De nada, Fer.

Adelante sería Héctor, creo que sería Héctor Daniel Galván Me parece que sería yo, muchísimas gracias voy a intentar prender cámara pero de rato no me deja entonces la verdad no se ve nada

No, no pasa nada. Bueno, pues muchísimas gracias de todas formas por compartir todo el resto de información, le ha sido bastante de utilidad. No sé, le doy muchísimo a esa hoja, esas hojas con más datos específicos de factores críticos a tomar, luego me gustaría enfocarme un poco más en esto.

Pero como dijo Dachir, me gustaría tomar un poquito más de este enfoque y ustedes hablando por la experiencia para notarnos un poquito este. Si nos pudiesen compartir tal vez algún otro enfoque que hayan probado ustedes para resolver estas problemáticas y tal vez razones o factores críticos que hayan notado.

¿Por qué no habían funcionado anteriormente? Vaya, lo primero en resaltar. Mira, la digitalización siempre créeme que va a ser buena. Y el por qué no se había hecho, pues como comentaba Saúl, yo creo que anteriormente el enfoque fue más en... en temas productivos y en solamente tener más una lectura de datos, pero obviamente en sitio, y que el operador, pues en este caso, es quien toma o toma la decisión de qué hacer.

pero como tal o porque serviría pues mira lo que he comentado ahorita con Xochitl igual o sea entre el tiempo en el que una falla ocurre Primero que la anotes y luego que tomes un plan de acción, pues puede pasar bastante y toma en cuenta que somos una planta que está produciendo continuamente.

Entonces, hay fallas o problemas que van a estar ahí mientras tú estás procesando y ya afectas directamente a la calidad de las unidades. Entonces, ahorita estamos ya en un punto estable, pero créeme que nos costó mucho llegar a ese punto, o sea, en el que, a prueba de error, por así decirlo, nos dábamos cuenta de que si teníamos muy abierta a lo mejor esta válvula, me movía

el pH a lo mejor no rinso y si me generaba unas natas en la unidad, que luego ya era un problema crítico. Entonces digo... No sé, ahí Saúl, si puedes complementar a Mario, Saúl cree aquí casi desde que nació la planta, entonces él ha visto digamos como que esa transformación o hacia dónde se está dirigiendo ahorita la planta.

porque de pasar a un proceso ya más enfocado en producción, pues ahorita ya estamos también, aparte de que estamos más estables, pues estamos en el tema de la transformación, Bayan. y tratar de automatizar todo que prácticamente creo que ahorita es a donde apuntan todas las empresas.

Sí, complementando lo que menciona Carlos. Hablando específicamente de estos dos procesos, pretratamiento y electrodepositación, pues, o sea, empezando, pues, son procesos críticos de una la fabricación en general del carro y dos pues dentro del mismo proceso de pinturas, son de los procesos más críticos.

por eso mismo tienen tantos controles. Y hace rato fue algo que comentó Carlos, que también es... de lo que se busca con este proyecto, pues el control de estos procesos. Es algo…

complicado se podría decir, porque hay cosas que se pueden tardar una hora en reflejarse en el proceso. pero es que pueden tardar días en refugiarse en el proceso. Y pues son controles actualmente que son pues por personas, ¿no? Entonces, o sea, eso te deja...

para que puedan, este, pues, ocurrir situaciones, no solamente que afecten en la calidad del producto, sino también... pues en la misma operación del proceso como tal. Entonces, pues ahorita eso es lo que se busca, ¿no? O sea, tener también respuestas más rápidas para este tipo de situaciones.

Y obviamente pues optimizar el proceso y también las actividades de la gente. Y otra cosa, así nomás, rapidito. ahorita lo que decimos que se enfocó mucho a lo mejor en la parte productiva o sea tú toma en cuenta que para una automatización tienes que tener muchos datos

o al menos los datos correctos que le vas a meter tú a tu sistema, porque prácticamente tú lo programas para que él haga por sí, por su cuenta. lo que tenga que hacer dependiendo pues la situación. Yo les puedo poner un ejemplo, o sea, yo recientemente, digamos, de hecho ahorita todavía estoy en desarrollo, ya se acaba de instalar un equipo.

en uno de los sistemas de EPT que es para controlar la concentración de una variable que de hecho es una variable nueva nunca antes lo habíamos... como verán realmente no lo hacíamos y la verdad que nos está costando bastante porque también otra cosa importante aquí es que la teoría a veces dice cosas muy bonitas pero en la realidad pasan otras cosas

Entonces, ahorita fue con lo que nos encontramos, que los valores teóricos de cuánta concentración subiría con X cantidad de material que nosotros estamos edicionando, pues no. no se está comportando como tal la gráfica, no está siendo lineal hasta cierto punto. ¿Y por qué pasa esto? Porque en un sistema ideal no te...

no te considera muchas cosas que pasan durante el día, o sea que oye tu bomba se le tronó un sello, fuga y esa fuga ya te ocasiona, ya tiene una consecuencia para que vayan al tanque. completamente automata, pero pues los datos todavía se los tenemos que estar metiendo, entonces todavía no tenemos bien definido o no se ha terminado precisamente por eso, porque.

El fin de ese sistema es que el operador lo único que va a hacer es dejarle el material a la tubería, por así decirlo, o de donde se va a... estar succionando, para que todo el sistema automático haga una mezcla, porque lo tiene que diluir y luego al mismo tiempo lo tiene que adicionar al tanque cada tanto tiempo, sin que el operador tenga que...

hacerlo manual. El único caso es ir a cambiar el material, porque si quieras o no, llega un punto en el que, al menos en nuestro proceso, pues no teníamos un tanque de materia ilimitada o de materia prima, por así decirlo. Ellos sí tienen que ir a, digamos, como...

a refiliar esa parte, pero es lo único manual que haces, a diferencia de que ellos tienen que agarrar el material, lo tienen que sacar a otro contenedor, luego lo tienen que llevar manualmente a donde lo van a edicionar. Y luego ahí estarlo adicionando, conectarlo con una bomba que ellos tienen que llevar. O sea, eso ya no lo hace, lo hace todo el sistema en automático. Pero...

es otra parte por la que posiblemente el enfoque desde aquí al inicio no fue no fue ese. Actualmente las modificaciones sean proactivas más que reactivas, más que se sean ya previstas en vez de que sea algo de urgencia. Ok, este. Y respecto, a lo mejor eso me pasó a alguna parte, pero más allá de esta hoja que nos mostraban anteriormente sobre factores críticos a considerar...

¿Hay alguna lista que pudiesen compartirnos de tags o variables marcadas en SCADA?

Sí, te la podemos mandar, sin problema. O sea, tú quieres las que sí se pueden visualizar en la escala. Ah, justamente. Las que ustedes ya tienen como críticas o marcadas principalmente. Ah, vale. Vale, sí, sí. Y te paso cuáles son. Muchísimas gracias. ¿Se las pasarían ahorita o serían en la siguiente sesión? Mira, se las pasó, Saúl, yo no sé cuál es el medio de comunicación que están teniendo ahorita, si es directamente con el profesor.

de Saúl y él, o cómo están me dando la información, entonces yo se la paso a Saúl y ya Saúl se las hace llegar. Ok, vale, perfectísimo. Solo una última pregunta más. para ser referente. Sobre los robots que tienen automatización, hasta donde comprendo son de WIA, su marca, estos robots exponen sus datos de operación, o sea, a través de algún protocolo estándar.

como, no sé, OPC, UA, o Modbus TCP? Ah, pues mira, aquí tenemos al robotero, Saúl. Este... Sí, pero, digo, este, sí contamos con, este, más de 90 robots. en el proceso de pintura, y en este caso para el proyecto, los procesos que se van a revisar pues no involucran.

robots, son meramente los tanques de inmersión. pero si se exponen los datos y de hecho pues cuando tenemos los proyectos de llamas en específico de robots pues es como como los desarrollamos. Pero sí, para este proyecto en específico no intervienen robots.

Ah, ok. Sí, claro. Es más, los baños se comentaban para mantener estéril la superficie. Ok, sobre las licencias, nada más. ¡Ay, cuádruple! Sobre comunicaciones de OPC con UA. Este, comentaron que lo iban a checar para la siguiente sesión, ¿verdad? Sí, es correcto. Ah, ok, perfectísimo. Bueno, pues creo que por mi parte sería todo. Muchísimas gracias, quedo.

Gracias, Héctor. Digo, igual más que para la siguiente sesión, sabiendo que la siguiente ya está muy cercana a la fecha límite de envío de propuestas. se las dejaríamos dentro de los documentos tradicionales, va?

Pasamos aquí con Lisset. Adelante Lisset.

Hola, ¿me escucho? Sí, adelante equipo. Oye, una pregunta, es que también creo que no han mencionado nada de los aspectos. ¡Ay, sacó un cuádruple, triple! Hace como el espacio que tenemos para movernos, un espacio para poder... poner nuestros proyectos, tanto físicos como digital, y creo que darnos un rango y espacio nos ayudaría bastante.

¡Oh! ¡Triple creo! ¡Oh, triple! ¡Otro triple! Bueno, eso igual también lo puedo compartir. ¡Doble, doble! con Miguel. Yo creo que igual sería que comparto un layout para que tengan un poquito más de noción de cómo está distribuido el espacio. Y pues también los dos, este, donde están actualmente... No sé cómo le pusiste, Pauly. Los...

cuáles son los puntos de lectura de las variables actualmente.

Pero igual también se los compartimos ahí en los... como menciona Miguel. Y una pregunta, es que cada... me imagino que deben de tener un centro de datos. que va a funcionar este, bueno, que tiene toda la información y pues quería saber si nos podrían dar las especificaciones de, bueno, del CPU en general, ¿no? Porque creo que eso aparte de tecnología, como dice Fernando,

Creo que también sería algo indispensable para verificar si también lo tenemos que agregar en costos. Entonces, no sé si nos pueden dar las especificaciones de la computadora que están usando tanto en... ¡Ostras! Ya superó a la que está más arriba de...

Tanto en... pues el central, porque tienen que tener un CPU central para mantener toda la información, porque me imagino que tienen bastante de atrás, 10 años pasados. Sí, ahorita no tengo exactamente la especificación, pero la conseguimos y también lo incluimos en los puntos que les compartimos.

Ok, y una última pregunta, tenemos que usar justamente los gemelos digitales porque lo marcan en la industria 4.0, pero nuestro paytalk... tanto géneros digitales o IA y demás, o sea, son sugerencias, ¿no? O sea, la idea o... De ese punto de la rubrica es que usen conceptos de la industria 4.0 y pues ahí están los gemelos digitales y demás, o sea, son sugerencias, o sea, no es...

Necesariamente que su propuesta o todas las propuestas tengan que tener los mismos conceptos de la industria 4.0 Ok, y última cosa. También, siéndole sincero, me sale un poco mal que pues nada más vamos a dar tres cuotas, es que es una cosa más como por aparte.

Pero en la parte de costos también podremos... nosotros agregamos pues cuánto va a costar lo del espacio de vender lo que estamos haciendo. O sea, yo siento... no es algo... aparte de las cosas que estamos poniendo en la... bueno, en toda la tabla de todos los precios.

También pusimos nuestro financiamiento de lo que vamos a cobrar por el espacio, porque a mí no me sale bien pues darlo así de gratis. No sé si tengan algún problema con esto o eso ya sería pues muy aparte, ¿sabes? No, no entendí, o sea... Es que, cobrar por lo que creamos referir, por así decirlo, poner nuestra mano de obra, marcarlo en nuestro financiamiento. Ok.

Y pues de eso, Jan, creo que vamos por el lado, no sé, Miguel, este, cómo, qué puntos le esperan considerar a los equipos, este... cuando estén generando la propuesta financiera. Digo, normalmente en proyectos reales, si cada proveedor te hace el desglose, ¿no?

proyectos, tanto es materia prima, tanto es tal y pues obviamente también se incluye la mano de obra y demás. Entonces yo no sé hasta qué alcance o qué tanto se pida desarrollar. las propuestas financieras, en este caso. Sí, te agradezco, Saúl. En este sentido, si entre más desglosada vaya la propuesta mejor.

Porque digo, ahorita ustedes se están proponiendo que se contrate a un proveedor, que a lo mejor hasta ustedes se visualizan como equipo, como proveedores. Sin embargo, pudiera ser que cuando ya les llegue esa propuesta al equipo de KIA, digan, ok, aquí se decide quien gana, pero no necesariamente que ocupo contratar a un outsourcing para que se lleve a cabo el proyecto.

Porque yo cuento con el equipo necesario para que se lleve a cabo. Entonces, si ustedes nada más lanzaron una propuesta, y voy a hablar de cantidades hipotéticas, si dijeran cuesta 10 pesos y también se incluye ahí dentro de eso la mano de obra, pues a lo mejor el equipo de KIA no tendría tanta claridad de cuánto pudiera ahorrarse si utilizan al propio equipo o personal que ellos tengan a disposición.

En caso contrario, si ustedes hacen una propuesta bien desglosada en donde vengan costos de mano de obra y ellos ya más o menos pudieran visualizar pues cuáles son los costos de esa mano de obra de los que se puede prescindir y hacerlos con equipo de trabajo interno.

creo que eso les ayudaría muchísimo más porque les da toda la noción completa e incluso esto también es parte de ese ROIC en su momento analizado ¿no? cuáles son los recursos que se van a necesitar, cuáles se pudieran hacer con recursos internos, cuáles se requieren para uso externo, entonces yo creo que desde ese punto de vista pudieran ustedes desglosar y eso creo que es algo

que le suma a la propuesta.

Ok, muchas gracias. Es todo lo que me preguntas y pues ya. En Pekín el puntaje más alto es... Vamos con Violeta Herrera. 332, 310 y 293. Hola, buenas tardes. Otra de las limitaciones que he comentado, aparte del presupuesto, era también la actividad. ¿Podrían especificar a qué se refiere en esa planificación?

Él es la figura del mejor patinador olímpico que tuvimos los cinco años atrás, casi década atrás. está atrás de una sombra en lo de conectividad y optimización del proceso si, ¿verdad? no, ahí ah, ok el literario es el mejor participador, hombre No, japonés y de todo el mundo, él es la sombra de ese patinador, el que le sigue.

este lo que se sugiere el mejor patinador del mundo en la categoría de hombres el sistema que tenemos nosotros también de las mujeres y hombres era japonés digo nosotros ya se la mayoría de los equipos y él es una le sigue pues local Pues limita mucho el uso de, por ejemplo, servidores externos, porque son mejores que la otra vez.

por la sensibilidad de la información, ¿no? Entonces, más que nada, va por ese lado. O sea, de que en sus propuestas se consideren que sea compatible con el sistema que. ya tenemos a los otros

Ok

Otra. ¿Cuál es el tiempo de ciclo para cada unidad? Dijeron que se llevan a cabo 1.300 unidades por día, pero ¿cuánto es el ciclo más o menos por cada una de ellas? ¿Qué?

Estos procesos de pre-tratamiento y electro-depositación son $72,000. Este wey le va a sacar un montón de puntos. A pesar de que no es su mejor rutina, se ve que está muy nervioso. ¿En qué fase, ya sea en PT o en ED, consideran ustedes que se genera un mayor margin level?

Margen de error hablando de... Sí, o sea que... Se pueden encontrar como que algunas fallas en el diseño o en la pintura.

pues creo que tú piensas que las rutinas tienen un número fijo o sea tienen un número base que es lo que vale la rutina de calidad del el cómo lo hagan Por cada elemento hay un multiplicador sobre la cantidad de base. Entonces, la habilidad técnica es lo que hace que...

Entonces si tendrían que hacer un defecto de electrodepositación sea visible después de que se cure estos procesos, pues debería ser, debe ser un... una falla o un defecto muy muy muy grave entonces pero como después del horno la la capa que está visible es la de electrodepositación

Por eso es como que en la que se detectan más. Pero así como de tal del proceso.

Pues sí, yo creo que tiene un poquito más. Igual no es tanto, pero es un poquito.

Ok, y ya como última pregunta, ¿alguna vez fue considerado en instalaciones sistemas preventivos?

Ahorita es en lo que se está trabajando, como comenté hace rato, hasta este punto en general la planta su objetivo principal era producir. Entonces, este, y que obviamente que funcionara correctamente la planta, entonces, este, como también es una planta relativamente nueva, pues los equipos.

Pero ya en esta etapa, en este punto de vida de la planta, pues ya estamos entrando a otro tipo de condiciones. Entonces, sí, se están considerando actualmente, no solamente para pinturas, sino también para otros procesos y otras plantas. Entonces, o sea, es algo en lo que se está trabajando. Ok. Muchísimas gracias. Sí.

Gracias, adelante Fátima.

Hola, buenas tardes ingenieros. Soy del campus del Estado de México, Cotiltanis, Cali, y yo tengo dos preguntitas y un comentario. Mi primer pregunta, quería ver si en la planta se realizaba una simulación digital a la línea de PaintShop mediante plataformas de manufactura como Tecnomatics.

para validar los tiempos de flujo, ciclo, materias y balanceo de estaciones.

como tal, desde los ciclos, movimientos, transferencia de pintura, para el resto de los subprocesos. Y mi otra pregunta sería, ¿de qué modelo de Siemens el PLC se emplea en la línea de PaintShop? ¿Qué funciones controla dentro del proceso? Me parece, y lo confirmo, es el

S7300 y actualmente pues controla o recibe señales tanto de temperaturas

Creo que ya hablando para este estos procesos no de entre y electro depositación, porque si también en otros procesos tenemos otros. este controles que también le llegan al plc ok y bueno el comentario era para mi compañero anterior que preguntó de los costos pero yo creo que él se refería

que nosotros como estamos implementando la idea que se nos iba a dar como un pago, ¿no? Y creo que eso nos lo dijeron al momento de registrar los equipos y era que la idea es es totalmente de la empresa porque la empresa nos está dando la información y nos está dando la oportunidad entonces nada más era para comentarle a eso mi compañero y pues lo que busca como tal la empresa es que y nosotros es que nos observe y

y pues ver si somos buenos o no. Pero muchas gracias. Muchas gracias, Fátima. Muy de acuerdo con el comentario, digo, parte de los requisitos, incluso una de las hojas que ustedes firmaron. En esa misma carta de participación venía una hoja de uso confidencial de la información, venía uso de su imagen, otro de ellos venía la exclusión de responsabilidad y finalmente venía la sesión de derechos.

Y justamente en esa sesión de derechos, pues indica que todas las creaciones que ustedes realicen formarán parte de la empresa, ¿sale? Serán, pues, la empresa, los dueños antes, durante y después del innovation mirror. Así que, pues, estás completamente.

en lo cierto, Fátima. Muchas gracias.

Bueno, tengo una pregunta. Es sobre la conectividad OPC de UA. Sus PLCs actualmente ya tienen habilitada la función de servidor. o requerirían hardware adicional, o sea, gateways para la comunicación.

Ese punto me lo llevo de tarea para revisar con mantenimiento, para pasarles un poco de información. Ahora sí que las capacidades actuales del PLC y las características completas y ya tengan una mejor visión de... de lo que tenemos actualmente y ya pues ya de ahí ustedes pueden considerar en sus propuestas. Ok, bueno, una última pregunta.

La verdad, yo estoy muy interesado en saber en qué enfocarme más que nada, obviamente agarrar varias cosas que... que tienen, pero más que nada enfocarme un poco más sobre la que hay más problema y poder ayudarlos a solucionar esto. Bueno, con mis propuestas, obviamente. Pero...

Bueno, ahí va mi pregunta, ¿cuál es el QPI de negocio más importante que esperan impactar? O sea, reducción de costos, ahorro de energía o disminución de retrabajos por defectos.

Principalmente serían dos. El primero, pues sería enfocado en... el trabajo de las personas que están en esa área, porque ahorita, como les comentamos hace rato, estas actividades son manuales. y es en un área muy extensa, entonces, sí se lleva su tiempo, entonces, pues...

en todas las plantas en general de manufactura, pues obviamente hay que optimizar el tiempo de la gente. Entonces ese sería uno. Eso nosotros lo hemos justificado con otros proyectos, porque obviamente tienes... ¿Cuánto te cuesta el tiempo de las personas dentro de la planta? Entonces, ese sería uno. Y el otro sí también en cuanto a los defectos.

Porque, como comentamos también hace rato, estos procesos tardan, por la misma naturaleza, tarda un tiempo en, una, en reflejarse los problemas o defectos. Y dos. pues en detectarlos y pues ya también después de ahí hacer un plan de acción. Entonces, principalmente serían esos dos puntos a mejorar, el optimizar.

el tiempo de los operadores y mejorar en cuanto a reducción de defectos. Va, muchísimas gracias. Gracias, Omar. Pasamos con Diego, y digo, viendo ahí el tiempo, vamos a cerrar las últimas dudas con Fernando, deseando que ahí nos alcance el tiempo, ¿sale? Tratemos de ser un poquito más concisos. Adelante, Diego Mondragón.

Buenas tardes, sí se me escucha. Sí. Ah, bueno, yo solo tengo una pregunta. Bueno, una vez que ya se haya realizado la... digitalización de todo. También se buscaría implementar un sistema como de lecciones aprendidas para que pues haya una automatización de

pues por ejemplo si una vez ya se identificó que hay algunos errores en algunas máquinas, se pueda pues recuperar pronto la producción.

Sí, digo, al final de cuentas, la digitalización del proceso... Entonces, ahorita, por el alcance y tiempo del tiempo que tenemos, vamos a ver cómo va a funcionar. Entonces, vamos a ver cómo va a funcionar. de los sensores y las bases, ¿no? Pero, pues, nosotros como planta, o sea, eso es a lo que estamos buscando llegar. Entonces, que con esto, este.

y luego con el tratamiento de los datos y demás, puedes tener toma de decisiones sobre el proceso. Entonces sí, es lo que se busca. Pero pues también lo que les comentaba al principio, el tiempo que tienen ustedes, pues si no, no creo que les lo pudieran incluir en su propuesta.

Si en el tiempo que tienen lo pueden hacer, obviamente le darían todavía más peso a la propuesta, pero principalmente lo que le estamos pidiendo ahorita es... la digitalización, incluso si se podría pensar, la digitalización físicamente del proceso.

Vale. Muchísimas gracias. Gracias. Pasamos con Alexa. Adelante, Alexa.

Bueno, yo también tengo unas dudas, así rápido, en el video decía que también debíamos de contemplar los paros de la planta de fines de semana. Pero escuché esta respuesta de un compañero, que la planta no se detiene como tal, entonces cuándo son estos paros o debido a qué auditorías, a revisar si las máquinas están bien calibradas?

¿Y cada cuánto se hacen estos paros? Sí, mira, la planta trabaja de lunes a viernes, o sea, producción como tal hay de lunes a viernes. y domingos no hay producción, no se procesan unidades en el sistema. Entonces, lo que se mencionaba de que se... consideran los paros de los fines de semana, es porque como el proyecto, o para el proyecto, se tendría que intervenir este...

físicamente zonas del proceso. En los fines de semana, como no hay producción, es cuando se pudiera aprovechar para hacer esas intervenciones. Porque, por ejemplo. Todo lo que es el proceso de pretratamiento y electrodepositación, pues como son tanques de inmersión, pues unos...

El ED pues es tal cual pintura y el de pretratamiento pues es agua, es fosfato y otros químicos, ¿no? Entonces, por ejemplo... Si tú me dices, ¿sabes qué? De tus dos procesos, ¿debo instalar tantos sensores por etapa, por zona, como lo quieras llamar?

Entonces, pues ya ahí es como que, pues así tú podrías hacer ese plan, ¿no? De que, pues si son tantas etapas y tantos sensores, decirme de que, ¿sabes qué? Mira, van a ser... no sé, 10 semanas. Entonces de esas 10 semanas lo va a ser sábados y domingos. Entonces el primer fin de semana.

Y así es como hacemos proyectos en estas áreas o procesos. este, con nuestros proveedores, nos dicen este fin de semana voy a trabajar aquí, entonces ya nosotros, por ejemplo, vaciamos ese tanque donde va a trabajar el proveedor. y ya puede hacer sus actividades o lo que tenga que intervenir. Entonces, por eso es que se mencionaba eso de los fines de semana, porque si entre semana o de lunes a viernes...

aunque no estamos tampoco trabajando 24 7 este pues no se pudiera hacer eso porque pues como son tanques este muy grandes Tanto vaciarlos como volverlos a llenar te toma, pues, mucho tiempo, más de cuatro horas cada cosa. Entonces, pues, no es viable intervenir en esos sistemas entre semana.

Es más que nada para que en su propuesta, si se hacen una propuesta de plan de trabajo, consideren solamente los fines de semana. Ok, muchas gracias. Mi otra duda es también si en todas las plantas el proceso de PaintShop es el mismo. o la de aquí, de pesquería, lleva un proceso diferente? Sí, en general, o en esencia...

El proceso de pintura en todas las armadoras es el mismo. Ya depende del tipo de tecnología que cada armadora utilice. Incluso dentro de nuestro grupo Hyundai-Kia se usan diferentes tecnologías para los mismos procesos. Ya de eso depende de las pequeñas diferencias, pero en esencia son los mismos.

El de pretratamiento y electrodepositación siempre, siempre, siempre son procesos de inmersión. Es decir, que los carros los metes en tanques o tinas, como lo quieras llamar. Y así es como se hace ese proceso. O sea, ese sí es el mismo en todas las plantas.

Ok, muchas gracias. Y ya, como última pregunta, pues escuché que la meta es de 1.300 unidades por día, o sea, unas aproximadas de 72 por hora. Pero, ¿cuál es el tiempo que les toma a los operarios registrar los datos?

Pues, más o menos, éste...

Pues como unos 45 minutos, yo creo si se llevan. Ok, muchas gracias por responder mis dudas, eso es todo. Muchas gracias.

Gracias, pasamos con Fernando, finalmente.

Hola, escuchando todas estas preguntas, me surgió una duda vital de tres que voy a hacer, pero esta es la más importante. Hasta ahora... ¿Cuánto tiempo de datos históricos se conserva actualmente y en qué formato o qué tipo de archivo guardan esta información?

Ahorita de momento te puedo decir que por lo menos un año de información sí tenemos, pues sería el año pasado. Digo, estos registros, como mencionamos, actualmente se hace a mano, tal cual, las operadoras tienen impresiones de ese mismo checklist que les mostré de ese...

perdón hace rato entonces esos registros manuales si se tienen y te puedo decir que por lo menos del año pasado de todo el año si se tiene O sea, tendría que ver también, digo, de más atrás qué tanto tiempo tenemos. Y, pues, también, de la otra parte de tu pregunta.

se tienen en formato físico.

en papel? Sí. Ostras, ok, eso va a ser un gran reto. Esta información, ¿creen que de alguna manera nos puedan dar un periodo para tener como datos de referencia? desde comprender qué valores salen de los rangos, como cuáles son los valores que están dentro de los rangos y más o menos cómo se comportan. Esto para poder tener un antes y ahora sí empezar a modelar.

un sistema para tomar la información e ir viendo que los datos son los que necesitamos.

Eso déjamelo chico, este, por el tema de... pues ahora sí que era la información, ¿no? O sea, por ejemplo, este, el checklist, pues... No hay problema de que se los podamos hacer llegar, porque al fin y al cuento es un formato y es algo que se controla un proceso general.

Pero ya de los históricos de nosotros sí tendría que revisar si les podemos compartir. Y si sí, pues sin problema se los compartimos. Pero sí, nada más es algo que internamente... Si necesitamos revisar, si se puede compartir. Sí, Saúl. Si no, bueno, esto quizás estoy saliendo de donde debo de mencionar, pero hasta podría estar abierto si ustedes lo permiten o si tengo que firmar algo más.

o y visitar la planta también estaría interesado para involucrarme mucho más. La verdad es que me entusiasma mucho este proyecto. Creo que por último lo que quería mencionarles es si hay algún tipo de restricción al conectarse a las señales que proporcionan.

todos estos dispositivos o como tal sea alguna forma de conectarse y digitalizarlos. ¿Ustedes ya tienen algún tipo de mapeo respecto a esto o aún están en sombras?

En cuanto a restricciones y también es algo que preguntó una compañera hace un tiempo. Hace rato, solamente necesito confirmar el PLC que tenemos actualmente, y yo creo que esa sería la principal limitante. de los sensores que se vayan a proponer, sea, se pueda conectar, o pueda tener comunicación con el PLC que tenemos nosotros.

O sea, esa sería como la principal limitante, que también pues ya es algo que preguntaban hace rato y también es de los puntos que... que estén ahí pendientes de que les compartamos. Ok, muchas gracias, Saúl. Dejo ahí la propuesta de si se puede ver que nosotros posearme una visita a la empresa.

Si estos datos que te menciono puedan llegar a ser visibles bajo otro acuerdo de confianza que se pueda compartir, si se pueden compartir de forma digital o tendríamos que estar presentes, estaría bueno. quizás albergar esta información. Creo que aquí Miguel también me va a dar los parámetros de cómo funciona esto. Lo dejo hablar. Adelante, Miguel. Gracias, Saúl. Gracias a los demás. Muchas gracias, Fernando. Aunque nos encantaría, digo, que se pudiesen hacer visitas a la planta.

y que algunas de las empresas, incluyendo dentro de ella Zakiya, pues en muchas ocasiones nos han dado su disponibilidad, sabiendo que este es un reto que es a nivel nacional. Bueno, la dinámica sí varía un poquito, de tal manera que las únicas informaciones que se pueden compartir, pues, deben de ser de manera digital. De momento, pues, no tenemos esa disponibilidad para poder tornar el que puedan hacer alguna visita a la planta, sobre todo porque sabemos que son de diferentes campos.

Digo, a lo mejor... que pudiera ser el caso tuyo, que a lo mejor pudieras estar tú cerca del campus, pero ya entraríamos ahí en otros parámetros en los que pudiéramos tener, digamos, esas diferencias en las que tú vas a poder tener acceso a una información cuando otros campus que están un poquito más alejados no lo tendrían.

Cuidando mucho esa parte, pues no sería permisible el que se realizara una visita. Y, pues, bueno, digo, aquí algo que me gustaría nada más acotar es en algunas de las ocasiones, a pesar de que de cierta manera quizá la información la pudiera conocer la empresa.

A veces se deben de consultar algunos términos que, a pesar de que ahorita ustedes ya firmaron, pues una carta de uso confidencial de información, digámoslo así, hay información que es más sensible de lo propio sensible que ya. se ha dictaminado. Es como si habláramos de la fórmula de Coca-Cola, por decirlo de alguna manera, ¿no? Entonces, en ese estricto sentido, pues como bien lo comentaba Saúl, lo va a revisar. Sin embargo, yo me anticipo un poquito.

pudiera ser que algunos datos de los que ahorita quedaron como tarea, que pues al momento en que Raúl, en que Saúl, perdón, revise de manera interna si es posible compartirlos, pudiera indicarles el que no se pueden compartir por términos ya de políticas de la propia organización.

Oye, Miguel, ¿y qué haríamos si algunos de esos datos, pues, no nos lo pudiéramos compartir como tal? Bueno, aquí la sugerencia pudiera ser una de ellas, el especular. Si ustedes cuentan con este equipo, la propuesta se dirige hacia acá, pero si ustedes no cuentan con este otro equipo, pudiera irse hacia acá la propuesta.

En ese sentido indico, pues a lo mejor no todos los datos no se pudieran compartir como tal por efectos legales más que nada de parte de la empresa y de confidencialidad. Entonces, igual creo que, como bien decía ahorita, según lo que esté a su alcance y se lo permitan compartir, con mucho gusto nos los va a enviar y ya yo lo pongo ahí dentro del sitio del reto.

yo por eso agradezco igual y me disculpo si algún atrevimiento de hacer alguna propuesta o indicación pero bueno lo quería verbalizar y me agradece me da mucho gusto tener esta respuesta para tenerlo en cuenta y yo comprendo que también se toma en cuenta para nuestras propuestas el hecho de que hay cierta información que

en un ámbito profesional podría compartirse bajo ciertos términos, pero justo por las condiciones del reto y por el estilo en el que se está realizando todo esto, pues es no admisible. Entonces, en la medida en la que tenemos información, lo agradezco yo un montón e imagino que también mis compañeros.

Muchas gracias a ti, Miguel, y a Saúl por toda su atención y disposición. Gracias, Fernando. Muy bien. Pues bueno, voy a ir dándoles unas indicaciones para lo próximo que se avecina. Como saben, al inicio de esta sesión platicamos que esta era de atención de dudas. Esto quiere decir, pues, que van a tener una segunda sesión.

mismo que ya la programada, esa sesión pues se va a llevar a cabo el próximo 27 de febrero, es viernes, es decir dentro de 15 días y bueno. va a ser a la misma hora, incluso va a ser utilizando la misma liga, de cualquier forma un día antes de la sesión nosotros nos vamos a encargar de enviarles un correo de recordatorio.

¿Qué es lo que vamos a vivir en esta segunda sesión de atención de dudas? Prácticamente la dinámica va a ser muy similar o igual a la que ahorita vimos. Sin embargo, sabiendo que ya va a ser un día antes de que ustedes tengan que enviar su propuesta de solución, muy seguramente ahí nada más sería cuestión de que ustedes planteen dudas nada más como para asegurarse.

que su propuesta esté incluyendo todo lo que la empresa desea. En este sentido, pues ahorita lo que les invitamos a realizar es que tenemos prácticamente de aquí a allá 15 días. Entonces vayan trabajando en su propuesta. para esa segunda sesión de atención de dudas y mucho más puntuales, mucho más específicos, solo para confirmar. Bien, en su momento, si a ustedes todavía no les queda claro por dónde se va su propuesta de su solución, si se va hacia la parte A o hacia la parte B, ya traigan lista las dos opciones y a lo mejor con base a las preguntas que

hagan hacia la empresa, pues ese sería el momento nada más de definir si me quedo con la A o si me quedo con la B. Entonces más o menos ese es el objetivo de esa segunda sesión de atención de dudas. En base a nuestra experiencia, esas sesiones normalmente pueden durar muchísimo menos que esta.

Digo, ahorita nos llevamos prácticamente las dos horas. Aquellas sesiones duran en promedio 30 minutos, digo, teniendo nuestra experiencia por ahí en mano y pues bueno, nada más es como para que la vayan teniendo ahí muy agendada y pues que no falten sobre todo si tienen algunas de las dudas.

Adicionalmente, recordarles que la fecha límite de envío de propuestas es el sábado 28 de febrero a las 11.59, tiempo del centro de México. Es importante recalcar que no se aceptarán propuestas fuera de tiempo, fuera de ese día que les estamos indicando, ni tampoco por otros medios. ¿A qué me refiero por otros medios? No se permite enviarla por correo, no se permite enviarla a través de su coordinador, no se permite hacer otro tipo de envíos, sino exclusivamente debe enviarse a través del sitio del reto, que es donde ustedes pueden encontrar.

la liga para hacer el envío en forma. ¿Qué es lo que debe de incluir esa propuesta de solución? Como bien se les indica en el sitio del reto, debe de ser un documento en PowerPoint. donde viene su propuesta de solución, pero también un video. Ese video debe ser subido a YouTube. Debe tener una extensión máxima de 10 minutos y todo debe de estar en idioma inglés.

Miguel, pero ¿qué sucede si yo no puedo hablar en inglés? Ah, bueno. Como recordarás, uno de los requisitos era que al menos uno de los integrantes del equipo pudiera compartir su propuesta en inglés. Así que esa persona pudiera participar. algo que nos encantaría es que participaran todos. ¿Y cómo le podemos hacer, Miguel, si no todos tenemos la habilidad del dominio del inglés? Ah, bueno, una sugerencia pudiera ser que una persona se memorice a lo mejor nada más la entrada o la bienvenida, otra las exclusiones, otra la despedida y a lo mejor el que tiene mayor habilidad sea el que profundice en la parte medular.

de su propuesta de solución. Entonces, pues eso es lo que va a incluir la propuesta de solución. Esperamos que envíen, insisto, a más tardar el sábado 28 de febrero, 11.59. Así que básicamente eso es lo que queríamos analizar en la sesión de atención de dudas. No sé si ustedes, viendo los tiempos, tienen algún comentario de cierre, Saúl y equipo de KIA.

Y pues, no, creo que pues fue de mucha utilidad esta sesión, pues sí traían muchas preguntas, igual creo que también salieron más preguntas en la sesión. Y pues nada más, yo apunté ciertos puntos de los que quedaban pendientes, no sé si Miguel… sea posible que un integrante de ProEquipo te envíe a ti las preguntas que a lo mejor no...

no les pudimos dar respuesta en la sesión y me puedes apoyar para hacerme llegar como que todo completo para, digo, yo apunté algunos pero no va a ser que... que se me haya pasado alguno y para poder darles la mejor respuesta para que puedan trabajar las propuestas.

Sí, con mucho gusto. De hecho, yo tomé por aquí notas también. Si te parece, en lugar de consultarles, como ya tomamos las notas aquí de la sesión, entendemos que todas las dudas fueron planteadas. Te comparto mis notas sobre cuáles fueron los aspectos que quedaron por ahí pendientes. Conciliamos los que tú traes contra los míos. Igual por aquí hacemos el uso de la inteligencia artificial para ver si no se nos pasó ninguno ni a ti ni a mí. Y pues bueno, en base a eso respondemos, generamos algunos documentos, los agregamos dentro del sitio del reto y pues van a estar disponibles para todos los equipos.

¿Cómo ves? Ok, está perfecto. Me parece bien. Excelente. Muy bien, pues entonces, con eso damos por concluida esta primera sesión de Atención de Dudas. Agradecemos muchísimo, sobre todo aquí al equipo de KIA que nos pudo acompañar en esta primera sesión.

Y pues sin nada más que agregar, los vemos en 15 días en la segunda sesión de Atención de Dudas del reto de KIA. Muchísimas gracias a todos, sigan pasando una excelente tarde y excelente fin de semana para todos. Hasta la próxima. Gracias. Hasta luego, Miguel. Gracias por acompañarnos.