package it.arcade;

import java.sql.*;
import java.time.*;
import java.util.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
class DataController {
    private final JdbcTemplate db;
    private final OffsetDateTime demoInstant;
    DataController(JdbcTemplate db,@Value("${arcade.demo.istante}") String demoInstant) {
        this.db=db; this.demoInstant="live".equals(demoInstant) ? null : OffsetDateTime.parse(demoInstant);
    }
    // The names are constants, never supplied by a request. All values are bound parameters.
    @GetMapping("/affluenza/padiglioni") List<Map<String,Object>> presenze(@RequestParam(required=false) OffsetDateTime istante) { return at("presenze_al",istante); }
    @GetMapping("/affluenza/andamento") List<Map<String,Object>> andamento(@RequestParam(required=false) OffsetDateTime istante) { return at("andamento_al",istante); }
    @GetMapping("/affluenza/ingressi") List<Map<String,Object>> ingressi(@RequestParam(required=false) OffsetDateTime istante) { return at("ingressi_al",istante); }
    @GetMapping("/affluenza/giornata") Map<String,Object> giornata(@RequestParam(required=false) OffsetDateTime istante) {
        var rows=at("giornata_al",istante);
        if(rows.isEmpty()) throw new ResponseStatusException(HttpStatus.NOT_FOUND,"Giornata non disponibile");
        return rows.getFirst();
    }
    private List<Map<String,Object>> at(String function, OffsetDateTime requested) {
        var instant=requested!=null ? requested : demoInstant==null ? OffsetDateTime.now(ZoneId.of("Europe/Rome")) : demoInstant;
        if(requested!=null && (requested.getYear()<2024 || requested.getYear()>2026))
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"Istante demo fuori dalle edizioni disponibili");
        return db.query("SELECT * FROM arcade."+function+"(?)",ROW,instant);
    }
    @GetMapping("/espositore/me/visite")
    List<Map<String,Object>> visite(@AuthenticationPrincipal Jwt jwt,@RequestParam int edizione) {
        checkEdition(edizione);
        return db.query("SELECT edizione,codice_stand,giorno,ora,scansioni FROM arcade.v_espositore_visite_ora WHERE id_espositore = ? AND edizione = ? ORDER BY giorno,ora,codice_stand",ROW,exhibitor(jwt),edizione);
    }
    @GetMapping("/espositore/me/riepilogo")
    Map<String,Object> riepilogo(@AuthenticationPrincipal Jwt jwt,@RequestParam int edizione,
            @RequestParam(required=false) String codiceStand) {
        checkEdition(edizione);
        if(codiceStand!=null && (codiceStand.isBlank() || codiceStand.length()>10))
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"Codice stand non valido");
        var rows=codiceStand==null ? riepiloghi(jwt,edizione) :
            db.query("SELECT * FROM arcade.v_espositore_riepilogo WHERE id_espositore = ? AND edizione = ? AND codice_stand = ?",ROW,exhibitor(jwt),edizione,codiceStand);
        if(rows.isEmpty()) throw new ResponseStatusException(HttpStatus.NOT_FOUND,"Nessun risultato per questa edizione");
        if(rows.size()>1) throw new ResponseStatusException(HttpStatus.CONFLICT,"Sono presenti più stand: seleziona lo stand per il riepilogo");
        return rows.getFirst();
    }
    @GetMapping("/espositore/me/riepiloghi")
    List<Map<String,Object>> riepiloghi(@AuthenticationPrincipal Jwt jwt,@RequestParam int edizione) {
        checkEdition(edizione);
        return db.query("SELECT * FROM arcade.v_espositore_riepilogo WHERE id_espositore = ? AND edizione = ? ORDER BY codice_stand",ROW,exhibitor(jwt),edizione);
    }
    @GetMapping("/espositore/me/confronto")
    List<Map<String,Object>> confronto(@AuthenticationPrincipal Jwt jwt) {
        return db.query("SELECT edizione,codice_stand,padiglione,mq,imponibile,visite,contatti,ingressi_padiglione FROM arcade.v_espositore_confronto WHERE id_espositore = ? ORDER BY edizione,codice_stand",ROW,exhibitor(jwt));
    }
    @GetMapping("/espositore/me/rinnovo")
    List<Map<String,Object>> rinnovo(@AuthenticationPrincipal Jwt jwt) {
        String id=exhibitor(jwt);
        return db.query("SELECT edizione_rinnovo,codice_stand,padiglione,mq,posizione,prezzo_area_stimato,prelazione_fino_al,gia_rinnovato FROM arcade.v_espositore_rinnovo WHERE id_espositore = ? AND edizione_rinnovo = (SELECT max(edizione)+1 FROM arcade.contratto WHERE id_espositore = ? AND stato = 'firmato') ORDER BY codice_stand",ROW,id,id);
    }
    @GetMapping("/espositore/me/contatti")
    Map<String,Object> contatti(@AuthenticationPrincipal Jwt jwt,@RequestParam int edizione,
            @RequestParam(defaultValue="0") int page,@RequestParam(defaultValue="50") int size) {
        checkEdition(edizione);
        if(page<0 || size<1 || size>200) throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"Paginazione non valida");
        String id=exhibitor(jwt);
        Long total=db.queryForObject("SELECT count(*) FROM arcade.v_contatti_espositore WHERE id_espositore = ? AND edizione = ?",Long.class,id,edizione);
        var rows=db.query("SELECT id_contatto,edizione,codice_stand,raccolto_il,email,fascia_eta,provincia,interesse FROM arcade.v_contatti_espositore WHERE id_espositore = ? AND edizione = ? ORDER BY raccolto_il,id_contatto LIMIT ? OFFSET ?",ROW,id,edizione,size,(long)page*size);
        long count=total==null?0:total;
        return Map.of("content",rows,"page",page,"size",size,"totalElements",count,"totalPages",(count+size-1)/size);
    }
    private static String exhibitor(Jwt jwt) {
        String id=jwt.getClaimAsString("idEspositore");
        if(id==null || id.isBlank()) throw new ResponseStatusException(HttpStatus.FORBIDDEN,"Account espositore non valido");
        return id;
    }
    private static void checkEdition(int edition) {
        if(edition<2024 || edition>2026) throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"Edizione non valida");
    }
    static final RowMapper<Map<String,Object>> ROW=(rs,index) -> {
        Map<String,Object> row=new LinkedHashMap<>();
        var meta=rs.getMetaData();
        for(int i=1;i<=meta.getColumnCount();i++) {
            String name=meta.getColumnLabel(i);
            if("id_espositore".equals(name)) continue;
            StringBuilder key=new StringBuilder(); boolean upper=false;
            for(char c:name.toCharArray()) { if(c=='_') upper=true; else { key.append(upper?Character.toUpperCase(c):c); upper=false; } }
            Object value;
            if(meta.getColumnType(i)==Types.TIMESTAMP_WITH_TIMEZONE) value=rs.getObject(i,OffsetDateTime.class);
            else if(meta.getColumnType(i)==Types.DATE) value=rs.getObject(i,LocalDate.class);
            else value=rs.getObject(i);
            row.put(key.toString(),value);
        }
        return row;
    };
}
