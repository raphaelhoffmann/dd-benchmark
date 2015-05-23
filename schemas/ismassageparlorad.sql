DROP TABLE IF EXISTS ismassageparlorad CASCADE;
CREATE UNLOGGED TABLE ismassageparlorad (
    id bigint,
    doc_id text,
    is_true boolean,
    features text[]
) DISTRIBUTE BY HASH (doc_id); 
