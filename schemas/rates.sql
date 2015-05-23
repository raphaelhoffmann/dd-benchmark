DROP TABLE IF EXISTS rates CASCADE;
CREATE UNLOGGED TABLE rates (
    -- id for random variable
    id bigint,
    -- document id
    doc_id text,
    -- sentence id
    sent_id int,
    -- indexes of the words composing the mention
    wordidxs int[],
    -- mention id
    mention_id text,
    -- mention type
    type text,
    -- entity
    entity text,
    -- words
    words text[],
    -- is this a correct mention?
    is_correct boolean,
    -- features for training
    features text[]
) DISTRIBUTE BY HASH (mention_id);
