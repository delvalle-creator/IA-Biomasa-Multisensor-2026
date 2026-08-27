<!DOCTYPE qgis><qgis version="3.34" styleCategories="Symbology">
  <!-- Cambio de biomasa, post menos pre (Mg/ha). Negativo = pérdida
       ADVERTENCIA: el modelo de altura subestima los arboles altos (sesgo medido
       de casi 10 m por encima de 15 m) y la alometria lo amplifica. Este mapa
       SUBESTIMA los rodales altos. Ver TP5_03 y TP5_04. -->
  <pipe><rasterrenderer type="singlebandpseudocolor" band="1" opacity="1">
    <rastershader><colorrampshader classificationMode="1" colorRampType="INTERPOLATED">
      <item value="-100" color="#67001f" label="-100"/>
      <item value="-25" color="#f4a582" label="-25"/>
      <item value="0" color="#f7f7f7" label="0"/>
      <item value="25" color="#92c5de" label="+25"/>
    </colorrampshader></rastershader>
  </rasterrenderer></pipe>
</qgis>
