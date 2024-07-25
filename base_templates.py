
cursor_query = \
    """               SELECT 
$sel_fields
               FROM $tabela 
$cond_fields"""


select_query = \
    """              SELECT
$sel_fields
               INTO
$host_fields
               FROM $tabela
$cond_fields"""


insert_query = \
    """               INSERT INTO $tabela 
                    (
$sel_fields
                     )
               VALUES
                    (
$host_fields
                     )"""


update_query = \
    """               UPDATE $tabela 
                    SET
$sel_fields
$cond_fields"""


delete_query = \
    """               DELETE FROM $tabela
$cond_fields"""


sum_query = \
    """               SELECT VALUE ( SUM( 
$sel_fields ), 0)
               INTO :W-VLR-TTL
               FROM $tabela 
$cond_fields"""


count_query = \
    """               SELECT COUNT(*)
               INTO: CONTA-$tabela
               FROM $tabela 
$cond_fields"""


valida_statement = \
    '''           IF $variavel $operador
              MOVE '$variavel'   TO W-CAMPO
              PERFORM 900-001-ERRO-001
           END-IF
      *
'''

