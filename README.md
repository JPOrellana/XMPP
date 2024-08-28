## Proyecto 1 - Redes
### CHAT XMPP
#### José Pablo Orellana - 21970

---

## Descripción del Proyecto

Este proyecto es un cliente de chat basado en el protocolo XMPP, desarrollado utilizando Python y la librería `slixmpp`. La aplicación permite a los usuarios conectarse a un servidor XMPP, gestionar su lista de contactos, intercambiar mensajes y realizar varias operaciones de gestión de cuentas como la eliminación de cuentas. La interfaz gráfica (GUI) está implementada utilizando `tkinter`, lo que ofrece una experiencia de usuario sencilla y directa.

---

## Funcionalidades Implementadas

### 1) **Inicio de Sesión**

#### Descripción:
El usuario puede iniciar sesión utilizando su `JID` (Jabber ID) y contraseña. La autenticación se realiza contra un servidor XMPP.

#### Detalles Técnicos:
- **Entrada:** Usuario ingresa su `JID` y `contraseña`.
- **Proceso:** Se crea una instancia de `XMPPClient`, que maneja la autenticación y la conexión con el servidor XMPP.
- **Salida:** Si la autenticación es exitosa, se habilitan las funciones de la aplicación como la lista de contactos, la opción de agregar contactos y más.

#### Cómo se utiliza:
1. Al iniciar la aplicación, se presenta una pantalla de inicio de sesión.
2. Ingrese su `JID` y `contraseña`.
3. Haga clic en el botón "Iniciar Sesión".

---

### 2) **Cierre de Sesión**

#### Descripción:
El usuario puede cerrar la sesión actual, lo que desconecta la cuenta del servidor XMPP y lo redirige a la pantalla de inicio de sesión.

#### Detalles Técnicos:
- **Proceso:** Al cerrar sesión, la conexión XMPP se desconecta limpiamente y la interfaz vuelve a la pantalla de inicio de sesión.
- **Salida:** El usuario es desconectado del servidor XMPP y se deshabilitan las opciones del menú que requieren autenticación.

#### Cómo se utiliza:
1. Después de iniciar sesión, en la barra de menú, haga clic en "Cerrar Sesión".
2. La aplicación volverá a la pantalla de inicio de sesión.

---

### 3) **Mostrar Listado de Contactos**

#### Descripción:
Una vez autenticado, el usuario puede ver su lista de contactos, excluyéndose a sí mismo.

#### Detalles Técnicos:
- **Proceso:** Después de la autenticación, la lista de contactos se recupera del servidor y se muestra en la interfaz gráfica.
- **Salida:** Se muestra una lista de contactos en la interfaz, que permite seleccionar y ver más detalles o iniciar una conversación.

#### Cómo se utiliza:
1. Inicie sesión en la aplicación.
2. La lista de contactos aparecerá automáticamente en la parte izquierda de la interfaz.

---

### 4) **Agregar Contacto**

#### Descripción:
El usuario puede agregar nuevos contactos a su lista.

#### Detalles Técnicos:
- **Entrada:** `JID` del contacto que se desea agregar.
- **Proceso:** Se envía una solicitud de suscripción al `JID` ingresado. Si la solicitud es aceptada, el contacto se agrega a la lista.
- **Salida:** El nuevo contacto se agrega y se muestra en la lista de contactos.

#### Cómo se utiliza:
1. Después de iniciar sesión, en la barra de menú, seleccione "Agregar Contacto".
2. Ingrese el `JID` del contacto que desea agregar y haga clic en "Agregar".

---

### 5) **Mostrar Información de Contacto**

#### Descripción:
El usuario puede ver el estado de presencia de un contacto específico.

#### Detalles Técnicos:
- **Entrada:** `JID` del contacto del cual se desea ver la información.
- **Proceso:** Se consulta el estado de presencia del contacto y se muestra al usuario.
- **Salida:** Se muestra el estado de presencia del contacto en una ventana emergente.

#### Cómo se utiliza:
1. Después de iniciar sesión, en la barra de menú, seleccione "Detalle Contacto".
2. Ingrese el `JID` del contacto y haga clic en "Consultar".

---

### 6) **Eliminar Mi Usuario**

#### Descripción:
El usuario puede eliminar su cuenta del servidor XMPP. Esta acción es irreversible y elimina la cuenta permanentemente.

#### Detalles Técnicos:
- **Entrada:** Confirmación del usuario para eliminar su cuenta.
- **Proceso:** Se envía una solicitud de eliminación de cuenta al servidor. Si la operación es exitosa, la cuenta se elimina y el usuario es desconectado.
- **Salida:** La cuenta del usuario se elimina del servidor XMPP.

#### Cómo se utiliza:
1. Después de iniciar sesión, en la barra de menú, seleccione "Eliminar Cuenta".
2. Confirme que desea eliminar su cuenta cuando se le solicite.

---

## Requisitos

- **Python 3.11.9**
- **Bibliotecas:** 
  - `slixmpp`
  - `tkinter` (incluido con Python)
- **Servidor XMPP:** Debe tener acceso a un servidor XMPP para utilizar la aplicación.
- Si no tienes la versión de python y te crea conflicto. Crea un entorno virutal con esa versión para ejecutarlo.

---

## Instalación

1. Clone este repositorio en su máquina local.
2. Instale las dependencias necesarias utilizando `pip`:
   ```bash
   pip install slixmpp

## Para ejecutar el programa ir a consola. Ingresar a la dirección de la carpeta GUI y ejecutar el siguiente código
   ```bash
   python principal.py
