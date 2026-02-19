# KIA Paint Shop IoT Dashboard

Dashboard web en React + TypeScript para visualizar datos en tiempo real del sistema IoT del Paint Shop de KIA.

## Características

- **Visualización de 100 variables** organizadas por área (Pre-Treatment, E-Coat, Production Control)
- **Gráficos en tiempo real** con Recharts mostrando últimos 60 minutos de datos
- **Panel de alarmas** con indicadores de severidad y función de reconocimiento
- **Estadísticas agregadas** (promedio, mín, máx, desviación estándar)
- **Auto-refresh** cada 30 segundos
- **Indicador de conexión** con el API

## Stack Tecnológico

- React 18
- TypeScript
- Tailwind CSS (estilos)
- Recharts (gráficos)
- TanStack Query (data fetching y cache)
- Axios (cliente HTTP)

## Estructura del Proyecto

```
dashboard/
├── src/
│   ├── components/          # Componentes React
│   │   ├── AlarmPanel.tsx          # Panel de alarmas con filtros
│   │   ├── ConnectionStatus.tsx    # Indicador de estado de conexión
│   │   ├── StatisticsCard.tsx      # Tarjeta de estadísticas
│   │   ├── VariableChart.tsx       # Gráfico de línea con umbrales
│   │   └── VariableList.tsx        # Lista de variables por área
│   ├── hooks/               # Custom hooks
│   │   └── useVariableData.ts      # Hooks para fetching con TanStack Query
│   ├── services/            # Servicios
│   │   └── api.ts                  # Cliente API con axios
│   ├── types/               # Definiciones de tipos TypeScript
│   │   └── index.ts                # Tipos de API, variables, alarmas, etc.
│   ├── App.tsx              # Componente principal con layout
│   ├── index.tsx            # Entry point
│   └── index.css            # Estilos globales con Tailwind
├── public/
│   └── index.html
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── .env.example             # Variables de entorno de ejemplo
```

## Configuración

### 1. Instalar dependencias

```bash
npm install
```

### 2. Configurar variables de entorno

Crear archivo `.env.local` basado en `.env.example`:

```bash
cp .env.example .env.local
```

Editar `.env.local` con los valores reales:

```env
REACT_APP_API_URL=https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/demo
REACT_APP_API_KEY=your-api-key-here
```

### 3. Ejecutar en desarrollo

```bash
npm start
```

El dashboard estará disponible en `http://localhost:3000`

### 4. Build para producción

```bash
npm run build
```

Los archivos optimizados se generarán en el directorio `build/`

## Componentes Principales

### VariableList

Lista todas las variables organizadas por área. Permite seleccionar una variable para ver sus detalles.

**Props:**
- `selectedVariableId`: ID de la variable seleccionada
- `onSelectVariable`: Callback al seleccionar una variable

### VariableChart

Muestra un gráfico de línea con los datos de los últimos 60 minutos de una variable, incluyendo líneas de referencia para umbrales de alarma.

**Props:**
- `variable`: Objeto Variable con metadata

### AlarmPanel

Panel de alarmas con filtros por estado (activas, reconocidas, resueltas). Permite reconocer alarmas activas.

**Features:**
- Indicadores visuales de severidad (warning/critical)
- Botón de reconocimiento para alarmas activas
- Auto-refresh cada 30 segundos

### StatisticsCard

Muestra estadísticas agregadas de una variable (promedio, mínimo, máximo, desviación estándar).

**Props:**
- `variableId`: ID de la variable
- `unit`: Unidad de medida

### ConnectionStatus

Indicador visual del estado de conexión con el API.

**Props:**
- `isConnected`: Estado de conexión
- `isError`: Estado de error

## Hooks Personalizados

### useVariables()

Obtiene la lista de todas las variables con auto-refresh cada 30 segundos.

### useVariableData(variableId, start, end, enabled)

Obtiene datos históricos de una variable en un rango de tiempo.

### useAlarms(status?)

Obtiene alarmas filtradas por estado con auto-refresh cada 30 segundos.

### useStatistics(variableId, enabled)

Obtiene estadísticas agregadas de una variable.

## API Client

El servicio `api.ts` proporciona un cliente axios configurado con:

- Base URL desde variables de entorno
- API key en header `x-api-key`
- Timeout de 30 segundos
- Interceptores para manejo de errores
- Métodos tipados para todos los endpoints

## Estilos

El dashboard usa Tailwind CSS para estilos con:

- Diseño responsive (mobile-first)
- Tema de colores consistente
- Componentes reutilizables
- Animaciones suaves

## Auto-refresh

Todos los datos se refrescan automáticamente cada 30 segundos usando TanStack Query:

- Variables: cada 30s
- Datos de sensores: cada 30s
- Alarmas: cada 30s
- Estadísticas: cada 30s

## Manejo de Errores

- Estados de loading con skeletons animados
- Mensajes de error descriptivos
- Retry automático (hasta 2 intentos)
- Fallback UI cuando no hay datos

## Deployment

El dashboard puede desplegarse en:

- **AWS Amplify** (recomendado para el prototipo)
- **S3 + CloudFront**
- **Netlify**
- **Vercel**

### Deployment en AWS Amplify

```bash
# Build
npm run build

# Deploy (configurar en Terraform o manualmente en consola)
aws amplify publish
```

## Requisitos Validados

Este dashboard implementa los siguientes requisitos del spec:

- ✅ **Req 6.1**: Mostrar 100 variables organizadas por área
- ✅ **Req 6.2**: Gráfico de línea con últimos 60 minutos
- ✅ **Req 6.3**: Panel de alarmas con indicadores de severidad
- ✅ **Req 6.4**: Botón de acknowledge para alarmas
- ✅ **Req 6.5**: Auto-refresh cada 30 segundos
- ✅ **Req 6.6**: Indicador de estado de conexión

## Notas de Implementación

- **MINIMAL**: Implementación enfocada en funcionalidad esencial
- **No routing**: Dashboard de página única (SPA simple)
- **No autenticación de usuario**: Solo API key para backend
- **No persistencia local**: Todos los datos vienen del API
- **Optimizado para demo**: Diseñado para demostración, no producción a gran escala
