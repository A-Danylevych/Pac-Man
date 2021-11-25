(defvar stats (cl-csv:read-csv #P "statistics.csv"))

(defun get-scores (list)
  (mapcar #'(lambda (item) (parse-float (car (cdr (cdr item))))) list)
  )

(defun get-times (list)
  (mapcar #'(lambda (item) (parse-float (car (cdr item)))) list)
  )

(defun expected-mean (list)
  (/ (apply '+ list) (length list)))

(defun square-list-elemetns (list)
    (mapcar #'(lambda (item) (expt item 2)) list))
  
(defun dispersion (list)
  (- (expected-mean (square-list-elemetns list))
     (expt (expected-mean list) 2)))

(write-line "expected score:")
(write (expected-mean (get-scores stats)))
(write-line " ")
(write-line "time dispersion: ")
(write (dispersion (get-times stats)))

