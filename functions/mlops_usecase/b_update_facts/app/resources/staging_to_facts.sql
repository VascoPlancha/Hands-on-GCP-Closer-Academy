MERGE `{table_target}` AS T
USING (
    SELECT
        ???
        IF(Survived = 1, True, False) AS Survived,
        ????
    FROM
        `{table_source}`
    WHERE run_hash = "{run_hash}"
    QUALIFY ROW_NUMBER() OVER (PARTITION BY PassengerId ORDER BY Survived DESC) = 1
) S
ON (
    S.PassengerId = T.PassengerId
)
WHEN NOT MATCHED BY TARGET THEN
INSERT (
    ???,
    ???,
    ...
)
VALUES (
    ???,
    ???,
    ...
)
