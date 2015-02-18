<?php
/**
 * @package     Dumpmon Scraper
 * @copyright   2015 Davide Tampellini - FabbricaBinaria
 * @license     GNU GPL version 3 or later
 */

namespace Dumpmon\Utils;

class Clioptions
{
    private $data = array();

    public function __construct($options, $definition)
    {
        // All the options are stored using the long form
        foreach($definition as $short => $long)
        {
            $short = str_replace(':', '', $short);
            $long  = str_replace(':', '', $long);

            if(isset($options[$short]) || isset($options[$long]))
            {
                $value = isset($options[$short]) ? $options[$short] : $options[$long];

                // When the option is set but no value is passed, the variable is set to false
                // We want it back to true, to avoid confusion
                if(empty($value))
                {
                    $value = true;
                }

                $this->data[$long] = $value;
            }
        }
    }

    public function __get($name)
    {
        if(isset($this->data[$name]))
        {
            return $this->data[$name];
        }

        return null;
    }
}