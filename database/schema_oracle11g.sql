--------------------------------------------------------------------------------
-- PROYECTO: Totem Retail - Modelo de Datos (Oracle 11g)
-- COMPAT: sin IDENTITY / sin IS JSON (usa SEQUENCE + TRIGGER, CLOB “libre”)
-- NOTA: id_sesion se maneja como VARCHAR2(36) (UUID desde la app)
--------------------------------------------------------------------------------

-- DROP TABLE recommendation_item CASCADE CONSTRAINTS;
-- DROP TABLE recommendation_set CASCADE CONSTRAINTS;
-- DROP TABLE evento CASCADE CONSTRAINTS;
-- DROP TABLE consulta_voz CASCADE CONSTRAINTS;
-- DROP TABLE deteccion CASCADE CONSTRAINTS;
-- DROP TABLE inventario CASCADE CONSTRAINTS;
-- DROP TABLE producto_variante CASCADE CONSTRAINTS;
-- DROP TABLE producto CASCADE CONSTRAINTS;
-- DROP TABLE categoria CASCADE CONSTRAINTS;
-- DROP TABLE sesion CASCADE CONSTRAINTS;
-- DROP TABLE dispositivo CASCADE CONSTRAINTS;
-- DROP TABLE tienda CASCADE CONSTRAINTS;
-- DROP SEQUENCE seq_tienda; DROP SEQUENCE seq_dispositivo; DROP SEQUENCE seq_categoria;
-- DROP SEQUENCE seq_producto; DROP SEQUENCE seq_producto_variante; DROP SEQUENCE seq_inventario;
-- DROP SEQUENCE seq_deteccion; DROP SEQUENCE seq_consulta_voz; DROP SEQUENCE seq_reco_set;
-- DROP SEQUENCE seq_reco_item; DROP SEQUENCE seq_evento;

--------------------------------------------------------------------------------
-- MAESTROS
--------------------------------------------------------------------------------
CREATE TABLE tienda (
  id_tienda   NUMBER       PRIMARY KEY,
  nombre      VARCHAR2(50) NOT NULL,
  ubicacion   VARCHAR2(100),
  region      VARCHAR2(50),
  timezone    VARCHAR2(50) DEFAULT 'America/Santiago'
);

CREATE SEQUENCE seq_tienda START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE OR REPLACE TRIGGER trg_tienda_bi
BEFORE INSERT ON tienda FOR EACH ROW
WHEN (NEW.id_tienda IS NULL)
BEGIN
  :NEW.id_tienda := seq_tienda.NEXTVAL;
END;
/

CREATE TABLE dispositivo (
  id_dispositivo NUMBER       PRIMARY KEY,
  id_tienda      NUMBER       NOT NULL,
  etiqueta       VARCHAR2(50),
  estado         VARCHAR2(10) DEFAULT 'active' CHECK (estado IN ('active','inactive')),
  api_key        RAW(16)      DEFAULT SYS_GUID(),
  created_at     TIMESTAMP    DEFAULT SYSTIMESTAMP,
  CONSTRAINT dispositivo_tienda_fk
    FOREIGN KEY (id_tienda) REFERENCES tienda(id_tienda)
);

CREATE SEQUENCE seq_dispositivo START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE OR REPLACE TRIGGER trg_dispositivo_bi
BEFORE INSERT ON dispositivo FOR EACH ROW
WHEN (NEW.id_dispositivo IS NULL)
BEGIN
  :NEW.id_dispositivo := seq_dispositivo.NEXTVAL;
END;
/

CREATE TABLE categoria (
  id_categoria NUMBER        PRIMARY KEY,
  nombre       VARCHAR2(50)  NOT NULL
);

CREATE SEQUENCE seq_categoria START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE OR REPLACE TRIGGER trg_categoria_bi
BEFORE INSERT ON categoria FOR EACH ROW
WHEN (NEW.id_categoria IS NULL)
BEGIN
  :NEW.id_categoria := seq_categoria.NEXTVAL;
END;
/

CREATE TABLE producto (
  id_producto  NUMBER         PRIMARY KEY,
  nombre       VARCHAR2(100)  NOT NULL,
  id_categoria NUMBER         NOT NULL,
  marca        VARCHAR2(60),
  created_at   TIMESTAMP      DEFAULT SYSTIMESTAMP,
  updated_at   TIMESTAMP      DEFAULT SYSTIMESTAMP,
  CONSTRAINT producto_categoria_fk
    FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria)
);

CREATE SEQUENCE seq_producto START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE OR REPLACE TRIGGER trg_producto_bi
BEFORE INSERT ON producto FOR EACH ROW
WHEN (NEW.id_producto IS NULL)
BEGIN
  :NEW.id_producto := seq_producto.NEXTVAL;
END;
/

CREATE TABLE producto_variante (
  id_variante  NUMBER        PRIMARY KEY,
  id_producto  NUMBER        NOT NULL,
  sku          VARCHAR2(40)  NOT NULL UNIQUE,
  talla        VARCHAR2(20),
  color        VARCHAR2(30),
  precio       NUMBER(10,2)  NOT NULL,
  image_url    VARCHAR2(400),
  created_at   TIMESTAMP     DEFAULT SYSTIMESTAMP,
  updated_at   TIMESTAMP     DEFAULT SYSTIMESTAMP,
  CONSTRAINT pv_producto_fk FOREIGN KEY (id_producto)
    REFERENCES producto(id_producto) ON DELETE CASCADE,
  CONSTRAINT pv_unique UNIQUE (id_producto, talla, color)
);
CREATE INDEX ix_pv_producto ON producto_variante(id_producto);

CREATE SEQUENCE seq_producto_variante START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE OR REPLACE TRIGGER trg_producto_variante_bi
BEFORE INSERT ON producto_variante FOR EACH ROW
WHEN (NEW.id_variante IS NULL)
BEGIN
  :NEW.id_variante := seq_producto_variante.NEXTVAL;
END;
/

--------------------------------------------------------------------------------
-- OPERACIONAL
--------------------------------------------------------------------------------
CREATE TABLE sesion (
  id_sesion      VARCHAR2(36) PRIMARY KEY,  -- UUID desde la app
  id_dispositivo NUMBER       NOT NULL,
  inicio         TIMESTAMP    DEFAULT SYSTIMESTAMP,
  termino        TIMESTAMP,
  canal          VARCHAR2(20), -- voz / tactil
  consent        NUMBER(1)     DEFAULT 0 CHECK (consent IN (0,1)),
  CONSTRAINT sesion_dispositivo_fk
    FOREIGN KEY (id_dispositivo) REFERENCES dispositivo(id_dispositivo)
);

CREATE TABLE inventario (
  id_inventario NUMBER       PRIMARY KEY,
  id_variante   NUMBER       NOT NULL,
  id_tienda     NUMBER       NOT NULL,
  cantidad      NUMBER       DEFAULT 0 NOT NULL,
  updated_at    TIMESTAMP    DEFAULT SYSTIMESTAMP,
  CONSTRAINT inventario_variante_fk FOREIGN KEY (id_variante)
    REFERENCES producto_variante(id_variante),
  CONSTRAINT inventario_tienda_fk   FOREIGN KEY (id_tienda)
    REFERENCES tienda(id_tienda),
  CONSTRAINT inventario_unique UNIQUE (id_tienda, id_variante)
);

CREATE SEQUENCE seq_inventario START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE OR REPLACE TRIGGER trg_inventario_bi
BEFORE INSERT ON inventario FOR EACH ROW
WHEN (NEW.id_inventario IS NULL)
BEGIN
  :NEW.id_inventario := seq_inventario.NEXTVAL;
END;
/

CREATE TABLE deteccion (
  id_deteccion    NUMBER       PRIMARY KEY,
  id_sesion       VARCHAR2(36) NOT NULL,
  fecha_hora      TIMESTAMP    DEFAULT SYSTIMESTAMP,
  prenda          VARCHAR2(50),
  color           VARCHAR2(50),
  rango_etario    VARCHAR2(20),  -- child / youth / adult / senior
  genero          VARCHAR2(20),  -- masculine / feminine / unknown
  color_dominante VARCHAR2(30),
  confianza       CLOB,          -- JSON libre (sin check en 11g)
  modelo_version  VARCHAR2(50),
  CONSTRAINT deteccion_sesion_fk FOREIGN KEY (id_sesion)
    REFERENCES sesion(id_sesion) ON DELETE CASCADE
);
CREATE INDEX ix_deteccion_sesion_fecha ON deteccion(id_sesion, fecha_hora);

CREATE SEQUENCE seq_deteccion START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE OR REPLACE TRIGGER trg_deteccion_bi
BEFORE INSERT ON deteccion FOR EACH ROW
WHEN (NEW.id_deteccion IS NULL)
BEGIN
  :NEW.id_deteccion := seq_deteccion.NEXTVAL;
END;
/

CREATE TABLE consulta_voz (
  id_consulta    NUMBER        PRIMARY KEY,
  id_sesion      VARCHAR2(36)  NOT NULL,
  fecha_hora     TIMESTAMP     DEFAULT SYSTIMESTAMP,
  transcripcion  CLOB,
  intencion      VARCHAR2(80),
  entidades      CLOB,         -- JSON libre
  confianza      CLOB,         -- JSON libre
  latencia_ms    NUMBER,
  exito          NUMBER(1)     CHECK (exito IN (0,1)),
  CONSTRAINT consulta_voz_sesion_fk FOREIGN KEY (id_sesion)
    REFERENCES sesion(id_sesion) ON DELETE CASCADE
);
CREATE INDEX ix_cv_sesion_fecha ON consulta_voz(id_sesion, fecha_hora);

CREATE SEQUENCE seq_consulta_voz START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE OR REPLACE TRIGGER trg_consulta_voz_bi
BEFORE INSERT ON consulta_voz FOR EACH ROW
WHEN (NEW.id_consulta IS NULL)
BEGIN
  :NEW.id_consulta := seq_consulta_voz.NEXTVAL;
END;
/

-- Recomendaciones: set (cabecera) + items (detalle)
CREATE TABLE recommendation_set (
  id_set     NUMBER        PRIMARY KEY,
  id_sesion  VARCHAR2(36)  NOT NULL,
  fecha_hora TIMESTAMP     DEFAULT SYSTIMESTAMP,
  estrategia VARCHAR2(50),
  CONSTRAINT reco_set_sesion_fk FOREIGN KEY (id_sesion)
    REFERENCES sesion(id_sesion) ON DELETE CASCADE
);

CREATE SEQUENCE seq_reco_set START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE OR REPLACE TRIGGER trg_reco_set_bi
BEFORE INSERT ON recommendation_set FOR EACH ROW
WHEN (NEW.id_set IS NULL)
BEGIN
  :NEW.id_set := seq_reco_set.NEXTVAL;
END;
/

CREATE TABLE recommendation_item (
  id_item     NUMBER       PRIMARY KEY,
  id_set      NUMBER       NOT NULL,
  id_variante NUMBER       NOT NULL,
  score       NUMBER(5,4),
  mostrado    NUMBER(1)    CHECK (mostrado IN (0,1)),
  clicado     NUMBER(1)    CHECK (clicado IN (0,1)),
  CONSTRAINT reco_item_set_fk FOREIGN KEY (id_set)
    REFERENCES recommendation_set(id_set) ON DELETE CASCADE,
  CONSTRAINT reco_item_var_fk FOREIGN KEY (id_variante)
    REFERENCES producto_variante(id_variante)
);
CREATE INDEX ix_reco_item_set ON recommendation_item(id_set);

CREATE SEQUENCE seq_reco_item START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE OR REPLACE TRIGGER trg_reco_item_bi
BEFORE INSERT ON recommendation_item FOR EACH ROW
WHEN (NEW.id_item IS NULL)
BEGIN
  :NEW.id_item := seq_reco_item.NEXTVAL;
END;
/

-- Eventos genéricos
CREATE TABLE evento (
  id_evento   NUMBER        PRIMARY KEY,
  id_sesion   VARCHAR2(36)  NOT NULL,
  fecha_hora  TIMESTAMP     DEFAULT SYSTIMESTAMP,
  tipo        VARCHAR2(40)  NOT NULL, -- view, click, dwell, oos, voice_ok, voice_fail...
  metadata    CLOB,
  CONSTRAINT evento_sesion_fk FOREIGN KEY (id_sesion)
    REFERENCES sesion(id_sesion) ON DELETE CASCADE
);
CREATE INDEX ix_evento_sesion_fecha ON evento(id_sesion, fecha_hora);

CREATE SEQUENCE seq_evento START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE OR REPLACE TRIGGER trg_evento_bi
BEFORE INSERT ON evento FOR EACH ROW
WHEN (NEW.id_evento IS NULL)
BEGIN
  :NEW.id_evento := seq_evento.NEXTVAL;
END;
/

--------------------------------------------------------------------------------
-- DATOS DE EJEMPLO (opcionales para probar)
--------------------------------------------------------------------------------
INSERT INTO tienda (nombre, ubicacion, region) VALUES ('Tienda Central', 'Av. Principal 123', 'RM');

INSERT INTO dispositivo (id_tienda, etiqueta)
SELECT id_tienda, 'Totem-Entrada' FROM tienda WHERE nombre = 'Tienda Central';

INSERT INTO categoria (nombre) VALUES ('Zapatillas');
INSERT INTO categoria (nombre) VALUES ('Poleras');
INSERT INTO categoria (nombre) VALUES ('Chaquetas');

INSERT INTO producto (nombre, id_categoria, marca)
SELECT 'Zapatilla Runner X', id_categoria, 'MarcaZ'
FROM categoria WHERE nombre = 'Zapatillas';

DECLARE
  v_id_producto NUMBER;
BEGIN
  SELECT id_producto INTO v_id_producto FROM producto WHERE nombre='Zapatilla Runner X';
  INSERT INTO producto_variante (id_producto, sku, talla, color, precio)
  VALUES (v_id_producto, 'SKU-RUNX-42-RED', '42', 'Rojo', 49990);
END;
/
COMMIT;
