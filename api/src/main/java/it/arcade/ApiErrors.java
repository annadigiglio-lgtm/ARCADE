package it.arcade;

import java.util.Map;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataAccessException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.http.converter.HttpMessageNotReadableException;

@RestControllerAdvice
class ApiErrors {
    @ExceptionHandler(ResponseStatusException.class)
    ResponseEntity<?> status(ResponseStatusException ex) { return error(ex.getStatusCode().value(),ex.getReason()); }
    @ExceptionHandler({MethodArgumentNotValidException.class,MissingServletRequestParameterException.class,MethodArgumentTypeMismatchException.class,HttpMessageNotReadableException.class})
    ResponseEntity<?> invalid(Exception ex) { return error(400,"Richiesta non valida"); }
    @ExceptionHandler(DataAccessException.class)
    ResponseEntity<?> database(DataAccessException ex) {
        // SQL exception messages may contain connection details or row data.
        LoggerFactory.getLogger(ApiErrors.class).warn("Database non disponibile ({})",ex.getClass().getSimpleName());
        return error(503,"Dati temporaneamente non disponibili");
    }
    private ResponseEntity<?> error(int status,String message) { return ResponseEntity.status(status).body(Map.of("status",status,"message",message==null?"Errore":message)); }
}
