SELECT `supplier`.`name`, COUNT(`machine`.`id`), COUNT(DISTINCT `maintenance`.`id`))
FROM `supplier`
JOIN `machine` ON `supplier`.`id` = `machine`.`id_supplier`
JOIN `maintenance` ON `machine`.`id` = `maintenance`.`id_machine`
GROUP BY `supplier`.`id` ;
